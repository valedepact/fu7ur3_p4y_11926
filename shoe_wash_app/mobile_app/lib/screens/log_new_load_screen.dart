import 'package:flutter/material.dart';

import '../services/data_service.dart';
import '../services/api_service.dart';
import '../models/customer.dart';
import '../models/item_class.dart';
import '../theme.dart';

class LogNewLoadScreen extends StatefulWidget {
  final DataService dataService;
  const LogNewLoadScreen({super.key, required this.dataService});
  @override
  State<LogNewLoadScreen> createState() => _LogNewLoadScreenState();
}

class _LogNewLoadScreenState extends State<LogNewLoadScreen> {
  final _phoneController = TextEditingController();
  final _nameController = TextEditingController();
  List<Customer> _customers = [];
  List<ItemClass> _itemClasses = [];
  Customer? _selectedCustomer;
  DateTime? _pickupDate;
  final Map<int, int> _quantities = {};
  String? _error;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    widget.dataService.getCustomers().then((c) => setState(() => _customers = c));
    widget.dataService.getItemClasses().then((c) => setState(() => _itemClasses = c));
  }

  List<Customer> get _matches {
    final q = _phoneController.text.trim();
    if (q.isEmpty || _selectedCustomer != null) return [];
    return _customers.where((c) => (c.phone ?? '').contains(q)).take(4).toList();
  }

  double get _total => _quantities.entries.fold(0.0, (sum, e) {
    final item = _itemClasses.firstWhere((c) => c.id == e.key);
    return sum + item.basePrice * e.value;
  });

  Future<void> _submit() async {
    final items = _quantities.entries.where((e) => e.value > 0).map((e) => LoadItemInput(itemClassId: e.key, quantity: e.value)).toList();
    if (items.isEmpty) { setState(() => _error = 'Select at least one item.'); return; }

    final customerName = _selectedCustomer?.name ?? _nameController.text.trim();
    final customerPhone = _selectedCustomer?.phone ?? _phoneController.text.trim();
    if (customerName.isEmpty) { setState(() => _error = 'Enter a customer name.'); return; }

    setState(() { _saving = true; _error = null; });
    try {
      await widget.dataService.createLoad(
        customerName: customerName, customerPhone: customerPhone.isEmpty ? null : customerPhone,
        items: items, expectedPickupDate: _pickupDate?.toIso8601String().split('T')[0],
      );
      if (context.mounted) Navigator.pop(context);
    } catch (e) {
      setState(() { _error = e.toString(); _saving = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Log New Load')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        if (_error != null) Text(_error!, style: const TextStyle(color: AppColors.danger)),
        const Text('Customer', style: TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        TextField(
          controller: _phoneController, enabled: _selectedCustomer == null,
          decoration: InputDecoration(
            prefixIcon: const Icon(Icons.phone), hintText: 'Search phone number...', border: const OutlineInputBorder(),
            suffixIcon: _selectedCustomer != null ? IconButton(icon: const Icon(Icons.close),
              onPressed: () => setState(() { _selectedCustomer = null; _phoneController.clear(); _nameController.clear(); })) : null,
          ),
          onChanged: (_) => setState(() {}),
        ),
        ..._matches.map((c) => Card(color: AppColors.successBg, child: ListTile(
          leading: const Icon(Icons.person, color: AppColors.success), title: Text(c.name), subtitle: Text(c.phone ?? ''),
          onTap: () => setState(() { _selectedCustomer = c; _phoneController.text = c.phone ?? ''; }),
        ))),
        if (_selectedCustomer == null && _phoneController.text.isNotEmpty && _matches.isEmpty)
          Padding(padding: const EdgeInsets.only(top: 8), child: TextField(
            controller: _nameController, decoration: const InputDecoration(labelText: 'New customer name', border: OutlineInputBorder(), isDense: true),
          )),
        const SizedBox(height: 20),
        const Text('Item Classes', style: TextStyle(fontWeight: FontWeight.bold)),
        const Text('Select items and quantity', style: TextStyle(fontSize: 12, color: AppColors.inkSoft)),
        const SizedBox(height: 8),
        ..._itemClasses.map((c) {
          final qty = _quantities[c.id] ?? 0;
          return Card(child: ListTile(
            title: Text(c.name), subtitle: Text('UGX ${c.basePrice.toStringAsFixed(0)}'),
            trailing: Row(mainAxisSize: MainAxisSize.min, children: [
              IconButton(icon: const Icon(Icons.remove_circle_outline), onPressed: qty > 0 ? () => setState(() => _quantities[c.id] = qty - 1) : null),
              Text('$qty'),
              IconButton(icon: const Icon(Icons.add_circle_outline), onPressed: () => setState(() => _quantities[c.id] = qty + 1)),
            ]),
          ));
        }),
        const SizedBox(height: 16),
        ListTile(title: const Text('Total Price', style: TextStyle(fontWeight: FontWeight.bold)), trailing: Text('UGX ${_total.toStringAsFixed(0)}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16))),
        const SizedBox(height: 8),
        OutlinedButton(
          onPressed: () async {
            final picked = await showDatePicker(context: context, initialDate: DateTime.now(), firstDate: DateTime.now(), lastDate: DateTime.now().add(const Duration(days: 60)));
            if (picked != null) setState(() => _pickupDate = picked);
          },
          child: Text(_pickupDate == null ? 'Expected Pickup Date (optional)' : _pickupDate.toString().split(' ')[0]),
        ),
        const SizedBox(height: 20),
        FilledButton(onPressed: _saving ? null : _submit, child: Text(_saving ? 'Saving...' : 'Log Load')),
      ]),
    );
  }
}