import 'package:flutter/material.dart';

import '../services/data_service.dart';
import '../services/api_service.dart';
import '../models/pickup_request.dart';
import '../models/item_class.dart';
import '../theme.dart';

class PickupRequestConfirmScreen extends StatefulWidget {
  final DataService dataService;
  final PickupRequest request;
  const PickupRequestConfirmScreen({super.key, required this.dataService, required this.request});
  @override
  State<PickupRequestConfirmScreen> createState() => _PickupRequestConfirmScreenState();
}

class _PickupRequestConfirmScreenState extends State<PickupRequestConfirmScreen> {
  DateTime? _scheduledDate;
  List<ItemClass> _itemClasses = [];
  final Map<int, int> _quantities = {};
  String? _error;

  @override
  void initState() {
    super.initState();
    if (widget.request.status == 'confirmed') {
      widget.dataService.getItemClasses().then((c) => setState(() => _itemClasses = c));
    }
  }

  Future<void> _confirm() async {
    if (_scheduledDate == null) { setState(() => _error = 'Pick a date.'); return; }
    try {
      await widget.dataService.confirmPickupRequest(widget.request.id, _scheduledDate!.toIso8601String().split('T')[0]);
      if (context.mounted) Navigator.pop(context);
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  Future<void> _collect() async {
    final items = _quantities.entries.where((e) => e.value > 0).map((e) => LoadItemInput(itemClassId: e.key, quantity: e.value)).toList();
    if (items.isEmpty) { setState(() => _error = 'Select at least one item collected.'); return; }
    try {
      await widget.dataService.collectPickupRequest(widget.request.id, items, null);
      if (context.mounted) Navigator.pop(context);
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  Future<void> _cancel() async {
    await widget.dataService.cancelPickupRequest(widget.request.id);
    if (context.mounted) Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final r = widget.request;
    return Scaffold(
      appBar: AppBar(title: Text('Pickup Request \u2014 ${r.customerName}')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        if (_error != null) Text(_error!, style: const TextStyle(color: AppColors.danger)),
        ListTile(title: const Text('Phone'), subtitle: Text(r.phone)),
        ListTile(title: const Text('Address'), subtitle: Text(r.address)),
        if (r.notes != null) ListTile(title: const Text('Notes'), subtitle: Text(r.notes!)),
        const SizedBox(height: 16),
        if (r.status == 'requested') ...[
          const Text('Confirm & Schedule', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          OutlinedButton(
            onPressed: () async {
              final picked = await showDatePicker(context: context, initialDate: DateTime.now(), firstDate: DateTime.now(), lastDate: DateTime.now().add(const Duration(days: 30)));
              if (picked != null) setState(() => _scheduledDate = picked);
            },
            child: Text(_scheduledDate == null ? 'Pick a pickup date' : _scheduledDate.toString().split(' ')[0]),
          ),
          const SizedBox(height: 16),
          FilledButton(onPressed: _confirm, child: const Text('Confirm & Schedule')),
          const SizedBox(height: 8),
          OutlinedButton(onPressed: _cancel, child: const Text('Cancel Request')),
        ],
        if (r.status == 'confirmed') ...[
          Text('Scheduled: ${r.scheduledDate}', style: const TextStyle(color: AppColors.inkSoft)),
          const SizedBox(height: 12),
          const Text('What did you collect?', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          ..._itemClasses.map((c) {
            final qty = _quantities[c.id] ?? 0;
            return ListTile(title: Text(c.name), trailing: Row(mainAxisSize: MainAxisSize.min, children: [
              IconButton(icon: const Icon(Icons.remove_circle_outline), onPressed: qty > 0 ? () => setState(() => _quantities[c.id] = qty - 1) : null),
              Text('$qty'),
              IconButton(icon: const Icon(Icons.add_circle_outline), onPressed: () => setState(() => _quantities[c.id] = qty + 1)),
            ]));
          }),
          const SizedBox(height: 16),
          FilledButton(onPressed: _collect, child: const Text('Mark Collected')),
        ],
      ]),
    );
  }
}