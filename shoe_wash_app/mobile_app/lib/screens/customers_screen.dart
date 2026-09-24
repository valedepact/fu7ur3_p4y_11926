import 'package:flutter/material.dart';

import '../services/data_service.dart';
import '../models/customer.dart';

class CustomersScreen extends StatefulWidget {
  final DataService dataService;
  const CustomersScreen({super.key, required this.dataService});
  @override
  State<CustomersScreen> createState() => _CustomersScreenState();
}

class _CustomersScreenState extends State<CustomersScreen> {
  List<Customer> _customers = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    widget.dataService.getCustomers().then((c) => setState(() => _customers = c)).catchError((e) => setState(() => _error = e.toString()));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Customers')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
        ..._customers.map((c) => Card(child: ListTile(title: Text(c.name), subtitle: Text(c.phone ?? '--')))),
      ]),
    );
  }
}