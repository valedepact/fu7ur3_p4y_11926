import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../services/data_service.dart';
import '../theme.dart';

// The design shows four icons (Water, Power, Soap, Other) but the backend
// only has three categories (utilities covers both water and power).
const _options = [
  {'label': 'Water', 'icon': Icons.water_drop, 'category': 'utilities'},
  {'label': 'Power', 'icon': Icons.bolt, 'category': 'utilities'},
  {'label': 'Soap', 'icon': Icons.local_laundry_service, 'category': 'supplies'},
  {'label': 'Other', 'icon': Icons.more_horiz, 'category': 'other'},
];

class LogExpenseScreen extends StatefulWidget {
  final DataService dataService;
  const LogExpenseScreen({super.key, required this.dataService});
  @override
  State<LogExpenseScreen> createState() => _LogExpenseScreenState();
}

class _LogExpenseScreenState extends State<LogExpenseScreen> {
  final _amountController = TextEditingController(text: '0');
  String _category = 'utilities';
  DateTime _date = DateTime.now();
  String? _error;
  bool _saving = false;

  Future<void> _submit() async {
    final amount = double.tryParse(_amountController.text);
    if (amount == null || amount <= 0) { setState(() => _error = 'Enter a valid amount.'); return; }
    setState(() { _saving = true; _error = null; });
    try {
      await widget.dataService.createExpense(category: _category, amount: amount);
      if (context.mounted) Navigator.pop(context);
    } catch (e) {
      setState(() { _error = e.toString(); _saving = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    final isToday = DateFormat('yyyy-MM-dd').format(_date) == DateFormat('yyyy-MM-dd').format(DateTime.now());
    return Scaffold(
      appBar: AppBar(title: const Text('Log Expense')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        if (_error != null) Text(_error!, style: const TextStyle(color: AppColors.danger)),
        const Text('Amount', style: TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        TextField(controller: _amountController, keyboardType: TextInputType.number, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            decoration: const InputDecoration(prefixText: 'UGX ', border: OutlineInputBorder())),
        const SizedBox(height: 20),
        const Text('Category', style: TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        GridView.count(crossAxisCount: 4, shrinkWrap: true, physics: const NeverScrollableScrollPhysics(), mainAxisSpacing: 8, crossAxisSpacing: 8,
          children: _options.map((o) {
            final selected = _category == o['category'];
            return GestureDetector(
              onTap: () => setState(() => _category = o['category'] as String),
              child: Container(
                decoration: BoxDecoration(color: selected ? AppColors.primary : Colors.white,
                    border: Border.all(color: selected ? AppColors.primary : const Color(0xFFE2E8F0)), borderRadius: BorderRadius.circular(10)),
                child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                  Icon(o['icon'] as IconData, color: selected ? Colors.white : AppColors.inkSoft),
                  const SizedBox(height: 4),
                  Text(o['label'] as String, style: TextStyle(fontSize: 11, color: selected ? Colors.white : AppColors.inkSoft)),
                ]),
              ),
            );
          }).toList(),
        ),
        const SizedBox(height: 20),
        const Text('Date', style: TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        Row(children: [
          Expanded(child: OutlinedButton(
            onPressed: () async {
              final picked = await showDatePicker(context: context, initialDate: _date, firstDate: DateTime.now().subtract(const Duration(days: 365)), lastDate: DateTime.now());
              if (picked != null) setState(() => _date = picked);
            },
            child: Text(DateFormat('d MMM yyyy').format(_date)),
          )),
          if (!isToday) ...[const SizedBox(width: 8), TextButton(onPressed: () => setState(() => _date = DateTime.now()), child: const Text('Today'))],
        ]),
        const SizedBox(height: 20),
        FilledButton(onPressed: _saving ? null : _submit, style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(48)), child: Text(_saving ? 'Saving...' : 'Log Expense')),
      ]),
    );
  }
}