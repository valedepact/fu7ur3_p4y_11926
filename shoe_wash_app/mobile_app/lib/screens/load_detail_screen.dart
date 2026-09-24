import 'package:flutter/material.dart';

import '../services/data_service.dart';
import '../services/local_store.dart';
import '../models/load.dart';
import '../models/customer.dart';
import '../models/item_class.dart';
import '../utils/labels.dart';
import '../theme.dart';

const _flow = ['dropped_off', 'washing', 'ready'];

class LoadDetailScreen extends StatefulWidget {
  final DataService dataService;
  final Load load;
  const LoadDetailScreen({super.key, required this.dataService, required this.load});
  @override
  State<LoadDetailScreen> createState() => _LoadDetailScreenState();
}

class _LoadDetailScreenState extends State<LoadDetailScreen> {
  late Load _load;
  List<ItemClass> _itemClasses = [];
  Customer? _customer;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load = widget.load;
    _loadExtras();
  }

  Future<void> _loadExtras() async {
    final itemClasses = await widget.dataService.getItemClasses();
    final customers = await widget.dataService.getCustomers();
    setState(() {
      _itemClasses = itemClasses;
      _customer = customers.firstWhere((c) => c.id == _load.customerId, orElse: () => Customer(id: _load.customerId, name: '#${_load.customerId}'));
    });
  }

  String _itemClassName(int id) => _itemClasses.firstWhere((c) => c.id == id, orElse: () => ItemClass(id: id, name: '#$id', basePrice: 0)).name;

  Load _copyWith({String? status, double? amountPaid, String? paymentStatus}) => Load(
    id: _load.id, droppedOffAt: _load.droppedOffAt, customerId: _load.customerId, items: _load.items,
    amountPaid: amountPaid ?? _load.amountPaid, status: status ?? _load.status,
    expectedPickupDate: _load.expectedPickupDate, paymentStatus: paymentStatus ?? _load.paymentStatus,
    deliveryMethod: _load.deliveryMethod, pickupAddress: _load.pickupAddress, deliveryAddress: _load.deliveryAddress,
  );

  Future<void> _advanceStatus() async {
    final next = {'dropped_off': 'washing', 'washing': 'ready', 'ready': _load.deliveryMethod == 'pickup_delivery' ? 'delivered' : 'picked_up'}[_load.status];
    if (next == null) return;
    try {
      await widget.dataService.updateLoadStatus(_load.id, next);
      setState(() => _load = _copyWith(status: next));
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  Future<void> _markPaid() async {
    try {
      await widget.dataService.markLoadPaid(_load.id);
      setState(() => _load = _copyWith(amountPaid: _load.total, paymentStatus: 'paid'));
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  void _showPartialPaymentSheet() {
    final controller = TextEditingController();
    showModalBottomSheet(context: context, isScrollControlled: true, builder: (context) => Padding(
      padding: EdgeInsets.only(left: 16, right: 16, top: 16, bottom: MediaQuery.of(context).viewInsets.bottom + 16),
      child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.stretch, children: [
        const Text('Log Partial Payment', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        Text('Remaining balance: UGX ${(_load.total - _load.amountPaid).toStringAsFixed(0)}'),
        const SizedBox(height: 12),
        TextField(controller: controller, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Amount received')),
        const SizedBox(height: 16),
        FilledButton(onPressed: () async {
          final amount = double.tryParse(controller.text);
          if (amount == null || amount <= 0) return;
          try {
            await widget.dataService.recordPayment(_load.id, amount);
            if (context.mounted) Navigator.pop(context);
            setState(() => _load = _copyWith(
              amountPaid: _load.amountPaid + amount,
              paymentStatus: (_load.amountPaid + amount) >= _load.total ? 'paid' : 'partial',
            ));
          } catch (e) {
            setState(() => _error = e.toString());
            if (context.mounted) Navigator.pop(context);
          }
        }, child: const Text('Log Payment')),
      ]),
    ));
  }

  @override
  Widget build(BuildContext context) {
    final owing = _load.total - _load.amountPaid;
    final pendingSync = LocalStore.pendingCount > 0;

    return Scaffold(
      appBar: AppBar(title: Text('Load #${_load.id}')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        if (_error != null) Text(_error!, style: const TextStyle(color: AppColors.danger)),
        Card(child: ListTile(leading: const CircleAvatar(child: Icon(Icons.person)), title: Text(_customer?.name ?? '...'), subtitle: Text(_customer?.phone ?? ''))),
        const SizedBox(height: 12),
        const Text('Items', style: TextStyle(fontWeight: FontWeight.bold)),
        ..._load.items.map((it) => ListTile(dense: true, title: Text('${it.quantity} \u00d7 ${_itemClassName(it.itemClassId)}'), trailing: Text('UGX ${it.total.toStringAsFixed(0)}'))),
        const Divider(),
        ListTile(title: const Text('Total Price', style: TextStyle(fontWeight: FontWeight.bold)), trailing: Text('UGX ${_load.total.toStringAsFixed(0)}', style: const TextStyle(fontWeight: FontWeight.bold))),
        Row(children: [
          Expanded(child: Text('Paid: UGX ${_load.amountPaid.toStringAsFixed(0)}', style: const TextStyle(color: AppColors.success))),
          if (owing > 0) Expanded(child: Text('Owing: UGX ${owing.toStringAsFixed(0)}', style: const TextStyle(color: AppColors.danger), textAlign: TextAlign.end)),
        ]),
        const SizedBox(height: 16),
        Row(children: [
          Expanded(child: _InfoTile(label: 'Dropped off', value: _load.droppedOffAt.split('T')[0])),
          Expanded(child: _InfoTile(label: 'Expected pickup', value: _load.expectedPickupDate ?? '--')),
        ]),
        const SizedBox(height: 16),
        const Text('Status', style: TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        _StatusStepper(current: _load.status, deliveryMethod: _load.deliveryMethod),
        const SizedBox(height: 16),
        if (!['picked_up', 'delivered', 'abandoned'].contains(_load.status))
          FilledButton(onPressed: _advanceStatus, child: Text(_load.status == 'ready'
              ? (_load.deliveryMethod == 'pickup_delivery' ? 'Mark as Delivered' : 'Mark as Picked Up')
              : 'Mark as ${statusLabels[{'dropped_off': 'washing', 'washing': 'ready'}[_load.status]] ?? ''}')),
        const SizedBox(height: 20),
        const Text('Payment', style: TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        if (_load.paymentStatus != 'paid')
          Row(children: [
            Expanded(child: OutlinedButton(onPressed: _markPaid, child: const Text('Mark as Paid'))),
            const SizedBox(width: 8),
            Expanded(child: OutlinedButton(onPressed: _showPartialPaymentSheet, child: const Text('Log Partial Payment'))),
          ])
        else
          const Text('Fully paid', style: TextStyle(color: AppColors.success)),
        if (pendingSync) ...[
          const SizedBox(height: 16),
          Container(padding: const EdgeInsets.all(12), decoration: BoxDecoration(color: AppColors.warningBg, borderRadius: BorderRadius.circular(8)),
            child: const Row(children: [
              Icon(Icons.sync, color: AppColors.warning, size: 18), SizedBox(width: 8),
              Expanded(child: Text('Some changes on this device are pending sync. This update will be synced when online.', style: TextStyle(fontSize: 12))),
            ]),
          ),
        ],
      ]),
    );
  }
}

class _InfoTile extends StatelessWidget {
  final String label, value;
  const _InfoTile({required this.label, required this.value});
  @override
  Widget build(BuildContext context) => Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
    Text(label, style: const TextStyle(fontSize: 11, color: AppColors.inkSoft)),
    Text(value, style: const TextStyle(fontWeight: FontWeight.w600)),
  ]);
}

class _StatusStepper extends StatelessWidget {
  final String current, deliveryMethod;
  const _StatusStepper({required this.current, required this.deliveryMethod});
  @override
  Widget build(BuildContext context) {
    final finalLabel = deliveryMethod == 'pickup_delivery' ? 'Delivered' : 'Picked Up';
    final steps = ['dropped_off', 'washing', 'ready', 'final'];
    final currentIndex = (current == 'picked_up' || current == 'delivered') ? 3 : _flow.indexOf(current);
    return Row(children: List.generate(steps.length, (i) {
      final done = i <= currentIndex;
      final label = i == 3 ? finalLabel : (statusLabels[steps[i]] ?? steps[i]);
      return Expanded(child: Column(children: [
        CircleAvatar(radius: 12, backgroundColor: done ? AppColors.success : const Color(0xFFE2E8F0),
            child: done ? const Icon(Icons.check, size: 14, color: Colors.white) : null),
        const SizedBox(height: 4),
        Text(label, style: TextStyle(fontSize: 10, color: done ? AppColors.ink : AppColors.inkSoft), textAlign: TextAlign.center),
      ]));
    }));
  }
}