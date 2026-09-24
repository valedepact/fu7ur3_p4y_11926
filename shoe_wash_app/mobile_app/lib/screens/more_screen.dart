import 'package:flutter/material.dart';

import '../services/data_service.dart';
import 'collect_and_deliver_screen.dart';
import 'customers_screen.dart';
import 'item_classes_screen.dart';
import 'settings_screen.dart';
import 'expenses_screen.dart';

class MoreScreen extends StatelessWidget {
  final DataService dataService;
  const MoreScreen({super.key, required this.dataService});

  @override
  Widget build(BuildContext context) {
    final items = <(String, IconData, WidgetBuilder)>[
      ('Collect & Deliver', Icons.local_shipping, (c) => CollectAndDeliverScreen(dataService: dataService)),
      ('Expenses', Icons.receipt_long, (c) => ExpensesScreen(dataService: dataService)),
      ('Customers', Icons.people, (c) => CustomersScreen(dataService: dataService)),
      ('Item Classes', Icons.category, (c) => ItemClassesScreen(dataService: dataService)),
      ('Business Settings', Icons.settings, (c) => SettingsScreen(dataService: dataService)),
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('More')),
      body: ListView(children: items.map((item) => ListTile(
        leading: Icon(item.$2), title: Text(item.$1), trailing: const Icon(Icons.chevron_right),
        onTap: () => Navigator.push(context, MaterialPageRoute(builder: item.$3)),
      )).toList()),
    );
  }
}