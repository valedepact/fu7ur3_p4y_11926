import 'package:flutter/material.dart';

import '../services/data_service.dart';
import '../models/expense.dart';
import '../utils/labels.dart';
import 'log_expense_screen.dart';

class ExpensesScreen extends StatefulWidget {
  final DataService dataService;
  const ExpensesScreen({super.key, required this.dataService});
  @override
  State<ExpensesScreen> createState() => _ExpensesScreenState();
}

class _ExpensesScreenState extends State<ExpensesScreen> {
  List<Expense> _expenses = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  Future<void> _refresh() async {
    final end = DateTime.now();
    final start = end.subtract(const Duration(days: 30));
    String iso(DateTime d) => d.toIso8601String().split('T')[0];
    try {
      final data = await widget.dataService.getExpenses(iso(start), iso(end));
      setState(() => _expenses = data);
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Expenses')),
      floatingActionButton: FloatingActionButton(
        onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => LogExpenseScreen(dataService: widget.dataService))).then((_) => _refresh()),
        child: const Icon(Icons.add),
      ),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
        ..._expenses.map((exp) => Card(child: ListTile(
          title: Text('${categoryLabels[exp.category] ?? exp.category} \u2014 UGX ${exp.amount.toStringAsFixed(0)}'),
          subtitle: Text('${exp.date}${exp.note != null ? '  \u2022  ${exp.note}' : ''}'),
        ))),
      ]),
    );
  }
}