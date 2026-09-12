import 'package:flutter/material.dart';

import '../services/data_service.dart';
import '../models/totals.dart';
import '../models/load.dart';
import '../utils/period.dart';
import '../widgets/period_tabs.dart';

class OverviewScreen extends StatefulWidget {
  const OverviewScreen({super.key});

  @override
  State<OverviewScreen> createState() => _OverviewScreenState();
}

class _OverviewScreenState extends State<OverviewScreen> {
  final _api = DataService();
  String _period = 'week';
  Totals? _totals;
  List<Load> _loads = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _refresh();
    _api.init();
  }

  Future<void> _refresh() async {
    final range = rangeForPeriod(_period);
    try {
      final totals = await _api.getTotals(range.startIso, range.endIso);
      final loads = await _api.getLoads(range.startIso, range.endIso);
      setState(() { _totals = totals; _loads = loads; _error = null; });
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    final today = DateTime.now();
    final pending = _loads.where((l) => l.status != 'picked_up').length;
    final overdue = _loads.where((l) {
      if (l.expectedPickupDate == null || l.status == 'picked_up') return false;
      final pickup = DateTime.parse(l.expectedPickupDate!);
      return pickup.isBefore(DateTime(today.year, today.month, today.day));
    }).length;

    return Scaffold(
      appBar: AppBar(title: const Text('Overview')),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
            PeriodTabs(period: _period, onChanged: (p) { setState(() => _period = p); _refresh(); }),
            const SizedBox(height: 16),
            if (_totals != null) ...[
              _MetricTile(label: 'Sales', value: _totals!.sales, color: Colors.green),
              _MetricTile(label: 'Expenses', value: _totals!.expenses, color: Colors.red),
              _MetricTile(label: 'Balance', value: _totals!.balance, color: Colors.black87),
            ],
            const SizedBox(height: 16),
            ListTile(title: const Text('Pending orders'), trailing: Text('$pending')),
            ListTile(title: const Text('Overdue pickups'),
                trailing: Text('$overdue', style: const TextStyle(color: Colors.red))),
          ],
        ),
      ),
    );
  }
}

class _MetricTile extends StatelessWidget {
  final String label;
  final double value;
  final Color color;

  const _MetricTile({required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        title: Text(label),
        trailing: Text(value.toStringAsFixed(0),
            style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 18)),
      ),
    );
  }
}