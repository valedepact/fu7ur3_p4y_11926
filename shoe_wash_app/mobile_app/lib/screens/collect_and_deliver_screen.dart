import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../services/data_service.dart';
import '../models/pickup_request.dart';
import '../models/load.dart';
import '../models/customer.dart';
import '../theme.dart';
import 'pickup_request_confirm_screen.dart';

class CollectAndDeliverScreen extends StatefulWidget {
  final DataService dataService;
  const CollectAndDeliverScreen({super.key, required this.dataService});
  @override
  State<CollectAndDeliverScreen> createState() => _CollectAndDeliverScreenState();
}

class _CollectAndDeliverScreenState extends State<CollectAndDeliverScreen> {
  List<PickupRequest> _confirmed = [];
  List<Load> _readyForDelivery = [];
  List<Customer> _customers = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  Future<void> _refresh() async {
    final today = DateFormat('yyyy-MM-dd').format(DateTime.now());
    final start = DateFormat('yyyy-MM-dd').format(DateTime.now().subtract(const Duration(days: 30)));
    try {
      final confirmed = await widget.dataService.getPickupRequests('confirmed');
      final loads = await widget.dataService.getLoads(start, today);
      final customers = await widget.dataService.getCustomers();
      setState(() {
        _confirmed = confirmed;
        _readyForDelivery = loads.where((l) => l.deliveryMethod == 'pickup_delivery' && l.status == 'ready').toList();
        _customers = customers;
        _error = null;
      });
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  String _customerName(int id) => _customers.firstWhere((c) => c.id == id, orElse: () => Customer(id: id, name: '#$id')).name;

  Future<void> _markDelivered(Load l) async {
    try {
      await widget.dataService.updateLoadStatus(l.id, 'delivered');
      _refresh();
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Collect & Deliver')),
      body: RefreshIndicator(onRefresh: _refresh, child: ListView(padding: const EdgeInsets.all(16), children: [
        if (_error != null) Text(_error!, style: const TextStyle(color: AppColors.danger)),
        const Text('Today\'s Scheduled Collections', style: TextStyle(fontWeight: FontWeight.bold)),
        const Text('Tap to mark as collected', style: TextStyle(fontSize: 12, color: AppColors.inkSoft)),
        const SizedBox(height: 8),
        ..._confirmed.map((r) => Card(child: ListTile(
          leading: const Icon(Icons.local_shipping, color: AppColors.primary), title: Text(r.customerName), subtitle: Text('${r.phone}\n${r.address}'), isThreeLine: true,
          trailing: FilledButton(child: const Text('Mark Collected'),
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => PickupRequestConfirmScreen(dataService: widget.dataService, request: r))).then((_) => _refresh())),
        ))),
        if (_confirmed.isEmpty) const Padding(padding: EdgeInsets.all(12), child: Text('Nothing scheduled today.', style: TextStyle(color: AppColors.inkSoft))),
        const SizedBox(height: 24),
        const Text('Ready for Delivery (Pickup & Deliver)', style: TextStyle(fontWeight: FontWeight.bold)),
        const Text('Tap to mark as delivered', style: TextStyle(fontSize: 12, color: AppColors.inkSoft)),
        const SizedBox(height: 8),
        ..._readyForDelivery.map((l) => Card(child: ListTile(
          leading: const Icon(Icons.check_circle_outline, color: AppColors.success), title: Text(_customerName(l.customerId)), subtitle: Text('Ready \u2014 ${l.deliveryAddress ?? ''}'),
          trailing: FilledButton(child: const Text('Mark Delivered'), onPressed: () => _markDelivered(l)),
        ))),
        if (_readyForDelivery.isEmpty) const Padding(padding: EdgeInsets.all(12), child: Text('Nothing ready for delivery.', style: TextStyle(color: AppColors.inkSoft))),
      ])),
    );
  }
}