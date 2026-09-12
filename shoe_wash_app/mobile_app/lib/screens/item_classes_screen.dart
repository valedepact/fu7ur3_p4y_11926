import 'package:flutter/material.dart';

import '../services/data_service.dart';
import '../models/item_class.dart';

class ItemClassesScreen extends StatefulWidget {
  const ItemClassesScreen({super.key});

  @override
  State<ItemClassesScreen> createState() => _ItemClassesScreenState();
}

class _ItemClassesScreenState extends State<ItemClassesScreen> {
  final _api = DataService();
  List<ItemClass> _itemClasses = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final itemClasses = await _api.getItemClasses();
      setState(() { _itemClasses = itemClasses; _error = null; });
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  void _showAddSheet() {
    final nameController = TextEditingController();
    final priceController = TextEditingController();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => Padding(
        padding: EdgeInsets.only(left: 16, right: 16, top: 16,
            bottom: MediaQuery.of(context).viewInsets.bottom + 16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('Add item class', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            TextField(controller: nameController, decoration: const InputDecoration(labelText: 'Name')),
            TextField(controller: priceController, decoration: const InputDecoration(labelText: 'Base price'), keyboardType: TextInputType.number),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: () async {
                if (nameController.text.isEmpty || priceController.text.isEmpty) return;
                await _api.createItemClass(nameController.text, double.parse(priceController.text));
                if (context.mounted) Navigator.pop(context);
                _load();
              },
              child: const Text('Add'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Item classes')),
      floatingActionButton: FloatingActionButton(onPressed: _showAddSheet, child: const Icon(Icons.add)),
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
            ..._itemClasses.map((c) => Card(child: ListTile(title: Text(c.name), trailing: Text(c.basePrice.toStringAsFixed(0))))),
          ],
        ),
      ),
    );
  }
}