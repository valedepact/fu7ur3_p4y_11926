import 'package:flutter/material.dart';

import '../services/data_service.dart';
import '../models/item_class.dart';

class ItemClassesScreen extends StatefulWidget {
  final DataService dataService;
  const ItemClassesScreen({super.key, required this.dataService});
  @override
  State<ItemClassesScreen> createState() => _ItemClassesScreenState();
}

class _ItemClassesScreenState extends State<ItemClassesScreen> {
  List<ItemClass> _itemClasses = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    widget.dataService.getItemClasses().then((c) => setState(() => _itemClasses = c)).catchError((e) => setState(() => _error = e.toString()));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Item Classes')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
        ..._itemClasses.map((c) => Card(child: ListTile(
          title: Text(c.name),
          subtitle: Text('Base UGX ${c.basePrice.toStringAsFixed(0)} \u00b7 Cost UGX ${c.unitCost.toStringAsFixed(0)} \u00b7 ${c.washMinutes} min'),
        ))),
      ]),
    );
  }
}