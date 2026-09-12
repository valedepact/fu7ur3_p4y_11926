import 'package:flutter/material.dart';

import '../services/data_service.dart';
import '../models/load.dart';
import '../models/item_class.dart';
import '../models/customer.dart';
import '../utils/period.dart';
import '../widgets/period_tabs.dart';

const _statuses = ['dropped_off', 'washing', 'ready', 'picked_up'];

class LoadsScreen extends StatefulWidget {
  const LoadsScreen({super.key});

  @override
  State<LoadsScreen> createState() => _LoadsScreenState();
}

class _LoadsScreenState extends State<LoadsScreen> {
  final _api = DataService();
  String _period = 'week';
  List<Load> _loads = [];
  List<ItemClass> _itemClasses = [];
  List<Customer> _customers = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  Future<void> _refresh() async {
    final range = rangeForPeriod(_period);
    try {
      final loads = await _api.getLoads(range.startIso, range.endIso);
      final itemClasses = await _api.getItemClasses();
      final customers = await _api.getCustomers();
      setState(() { _loads = loads; _itemClasses = itemClasses; _customers = customers; _error = null; });
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  String _itemClassName(int id) =>
      _itemClasses.firstWhere((c) => c.id == id, orElse: () => ItemClass(id: id, name: '#$id', basePrice: 0)).name;

  String _customerName(int id) =>
      _customers.firstWhere((c) => c.id == id, orElse: () => Customer(id: id, name: '#$id')).name;

  void _showLogLoadSheet() {
    final customerController = TextEditingController();
    final quantityController = TextEditingController();
    final priceController = TextEditingController();
    int? itemClassId = _itemClasses.isNotEmpty ? _itemClasses.first.id : null;
    DateTime? pickupDate;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) {
        return StatefulBuilder(builder: (context, setSheetState) {
          return Padding(
            padding: EdgeInsets.only(left: 16, right: 16, top: 16,
                bottom: MediaQuery.of(context).viewInsets.bottom + 16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text('Log a load', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 12),
                TextField(controller: customerController, decoration: const InputDecoration(labelText: 'Customer name')),
                DropdownButtonFormField<int>(
                  value: itemClassId,
                  decoration: const InputDecoration(labelText: 'Item class'),
                  items: _itemClasses.map((c) => DropdownMenuItem(value: c.id, child: Text(c.name))).toList(),
                  onChanged: (v) => setSheetState(() => itemClassId = v),
                ),
                TextField(controller: quantityController, decoration: const InputDecoration(labelText: 'Quantity'), keyboardType: TextInputType.number),
                TextField(controller: priceController, decoration: const InputDecoration(labelText: 'Price (optional)'), keyboardType: TextInputType.number),
                const SizedBox(height: 8),
                OutlinedButton(
                  onPressed: () async {
                    final picked = await showDatePicker(
                      context: context, initialDate: DateTime.now(),
                      firstDate: DateTime.now(), lastDate: DateTime.now().add(const Duration(days: 60)),
                    );
                    if (picked != null) setSheetState(() => pickupDate = picked);
                  },
                  child: Text(pickupDate == null ? 'Expected pickup date' : pickupDate.toString().split(' ')[0]),
                ),
                const SizedBox(height: 16),
                FilledButton(
                  onPressed: () async {
                    if (customerController.text.isEmpty || itemClassId == null || quantityController.text.isEmpty) return;
                    await _api.createLoad(
                      customerName: customerController.text,
                      itemClassId: itemClassId!,
                      quantity: int.parse(quantityController.text),
                      priceCharged: priceController.text.isNotEmpty ? double.parse(priceController.text) : null,
                      expectedPickupDate: pickupDate != null ? pickupDate!.toIso8601String().split('T')[0] : null,
                    );
                    if (context.mounted) Navigator.pop(context);
                    _refresh();
                  },
                  child: const Text('Log load'),
                ),
              ],
            ),
          );
        });
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Loads')),
      floatingActionButton: FloatingActionButton(onPressed: _showLogLoadSheet, child: const Icon(Icons.add)),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
            PeriodTabs(period: _period, onChanged: (p) { setState(() => _period = p); _refresh(); }),
            const SizedBox(height: 12),
            ..._loads.map((load) => Card(
              child: ListTile(
                title: Text('${_customerName(load.customerId)} — ${_itemClassName(load.itemClassId)} x${load.quantity}'),
                subtitle: Text('Total: ${load.total.toStringAsFixed(0)}  •  Pickup: ${load.expectedPickupDate ?? '--'}'),
                trailing: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    DropdownButton<String>(
                      value: load.status,
                      items: _statuses.map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
                      onChanged: (s) async { if (s == null) return; await _api.updateLoadStatus(load.id, s); _refresh(); },
                    ),
                    if (load.paymentStatus == 'owing')
                      TextButton(
                        onPressed: () async { await _api.markLoadPaid(load.id); _refresh(); },
                        child: const Text('Mark paid'),
                      )
                    else
                      const Text('paid'),
                  ],
                ),
              ),
            )),
          ],
        ),
      ),
    );
  }
}