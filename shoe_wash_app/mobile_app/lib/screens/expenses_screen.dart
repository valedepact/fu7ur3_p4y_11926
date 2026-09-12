import 'package:flutter/material.dart';

import '../services/data_service.dart';
import '../models/expense.dart';
import '../utils/period.dart';
import '../widgets/period_tabs.dart';

const _categories = ['supplies', 'utilities', 'machine_upkeep', 'other'];

class ExpensesScreen extends StatefulWidget {
  const ExpensesScreen({super.key});

  @override
  State<ExpensesScreen> createState() => _ExpensesScreenState();
}

class _ExpensesScreenState extends State<ExpensesScreen> {
  final _api = DataService();
  String _period = 'week';
  List<Expense> _expenses = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  Future<void> _refresh() async {
    final range = rangeForPeriod(_period);
    try {
      final expenses = await _api.getExpenses(range.startIso, range.endIso);
      setState(() { _expenses = expenses; _error = null; });
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  void _showLogExpenseSheet() {
    String category = _categories.first;
    final amountController = TextEditingController();
    final noteController = TextEditingController();

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
                const Text('Log an expense', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  value: category,
                  decoration: const InputDecoration(labelText: 'Category'),
                  items: _categories.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
                  onChanged: (v) => setSheetState(() => category = v!),
                ),
                TextField(controller: amountController, decoration: const InputDecoration(labelText: 'Amount'), keyboardType: TextInputType.number),
                TextField(controller: noteController, decoration: const InputDecoration(labelText: 'Note (optional)')),
                const SizedBox(height: 16),
                FilledButton(
                  onPressed: () async {
                    if (amountController.text.isEmpty) return;
                    await _api.createExpense(
                      category: category,
                      amount: double.parse(amountController.text),
                      note: noteController.text.isNotEmpty ? noteController.text : null,
                    );
                    if (context.mounted) Navigator.pop(context);
                    _refresh();
                  },
                  child: const Text('Log expense'),
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
      appBar: AppBar(title: const Text('Expenses')),
      floatingActionButton: FloatingActionButton(onPressed: _showLogExpenseSheet, child: const Icon(Icons.add)),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
            PeriodTabs(period: _period, onChanged: (p) { setState(() => _period = p); _refresh(); }),
            const SizedBox(height: 12),
            ..._expenses.map((exp) => Card(
              child: ListTile(
                title: Text('${exp.category} — ${exp.amount.toStringAsFixed(0)}'),
                subtitle: Text('${exp.date}${exp.note != null ? '  •  ${exp.note}' : ''}'),
              ),
            )),
          ],
        ),
      ),
    );
  }
}