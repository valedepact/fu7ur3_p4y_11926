import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../services/data_service.dart';
import '../models/load.dart';
import '../models/customer.dart';
import '../models/pickup_request.dart';
import '../theme.dart';
import 'log_new_load_screen.dart';
import 'log_expense_screen.dart';
import 'pickup_requests_screen.dart';
import 'load_detail_screen.dart';

class HomeScreen extends StatefulWidget {
  final DataService dataService;
  const HomeScreen({super.key, required this.dataService});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<Load> _todayLoads = [];
  List<Customer> _customers = [];
  List<PickupRequest> _pendingPickups = [];
  double _incomeToday = 0;
  String? _error;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  Future<void> _refresh() async {
    final today = DateFormat('yyyy-MM-dd').format(DateTime.now());
    try {
      final loads = await widget.dataService.getLoads(today, today);
      final customers = await widget.dataService.getCustomers();
      final pending = await widget.dataService.getPickupRequests('requested');
      final totals = await widget.dataService.getTotals(today, today);
      setState(() { _todayLoads = loads; _customers = customers; _pendingPickups = pending; _incomeToday = totals.sales; _error = null; });
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  String _customerName(int id) => _customers.firstWhere((c) => c.id == id, orElse: () => Customer(id: id, name: '#$id')).name;

  @override
  Widget build(BuildContext context) {
    final droppedOff = _todayLoads.length;
    final ready = _todayLoads.where((l) => l.status == 'ready').length;

    // "Needs attention" is approximated by sorting ready loads by drop-off
    // time (oldest first) -- we don't track the exact moment a load became
    // ready, only when it was dropped off.
    final needsAttention = _todayLoads.where((l) => l.status == 'ready').toList()
      ..sort((a, b) => a.droppedOffAt.compareTo(b.droppedOffAt));

    return Scaffold(
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: CustomScrollView(
          slivers: [
            SliverAppBar(
              backgroundColor: AppColors.primary,
              expandedHeight: 100,
              pinned: true,
              flexibleSpace: const FlexibleSpaceBar(
                titlePadding: EdgeInsets.only(left: 16, bottom: 16),
                title: Text('Good morning, Manager', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
              ),
            ),
            SliverPadding(
              padding: const EdgeInsets.all(16),
              sliver: SliverList(delegate: SliverChildListDelegate([
                if (_error != null) Text(_error!, style: const TextStyle(color: AppColors.danger)),
                Row(children: [
                  Expanded(child: _StatCard(label: 'Loads Dropped Off', value: '$droppedOff')),
                  const SizedBox(width: 10),
                  Expanded(child: _StatCard(label: 'Loads Ready', value: '$ready')),
                  const SizedBox(width: 10),
                  Expanded(child: _StatCard(label: 'Income Today', value: 'UGX ${_incomeToday.toStringAsFixed(0)}')),
                ]),
                const SizedBox(height: 16),
                Row(children: [
                  Expanded(child: _ActionButton(label: 'Log New Load', icon: Icons.add, color: AppColors.primary,
                      onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => LogNewLoadScreen(dataService: widget.dataService))).then((_) => _refresh()))),
                  const SizedBox(width: 10),
                  Expanded(child: _ActionButton(label: 'Log Expense', icon: Icons.receipt_long, color: AppColors.success,
                      onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => LogExpenseScreen(dataService: widget.dataService))).then((_) => _refresh()))),
                  const SizedBox(width: 10),
                  Expanded(child: _ActionButton(label: 'Pickup Requests', icon: Icons.local_shipping, color: const Color(0xFF7C3AED),
                      onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => PickupRequestsScreen(dataService: widget.dataService))).then((_) => _refresh()))),
                ]),
                const SizedBox(height: 16),
                Card(child: ListTile(
                  leading: const Icon(Icons.local_shipping_outlined, color: AppColors.primary),
                  title: const Text('Pickup Requests'),
                  subtitle: Text('${_pendingPickups.length} pending requests awaiting confirmation'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => PickupRequestsScreen(dataService: widget.dataService))).then((_) => _refresh()),
                )),
                if (needsAttention.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  const Text('Needs Attention', style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.danger)),
                  const SizedBox(height: 8),
                  ...needsAttention.take(3).map((l) => Card(
                    color: AppColors.dangerBg,
                    child: ListTile(
                      leading: const Icon(Icons.warning_amber, color: AppColors.danger),
                      title: Text(_customerName(l.customerId)),
                      subtitle: Text('${l.totalQuantity} item(s) \u2014 Ready'),
                      trailing: TextButton(child: const Text('View'),
                          onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => LoadDetailScreen(dataService: widget.dataService, load: l))).then((_) => _refresh())),
                    ),
                  )),
                ],
              ])),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label, value;
  const _StatCard({required this.label, required this.value});
  @override
  Widget build(BuildContext context) => Card(child: Padding(
    padding: const EdgeInsets.all(12),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
      const SizedBox(height: 4),
      Text(label, style: const TextStyle(fontSize: 11, color: AppColors.inkSoft)),
    ]),
  ));
}

class _ActionButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;
  const _ActionButton({required this.label, required this.icon, required this.color, required this.onTap});
  @override
  Widget build(BuildContext context) => Material(
    color: color, borderRadius: BorderRadius.circular(10),
    child: InkWell(borderRadius: BorderRadius.circular(10), onTap: onTap,
      child: Padding(padding: const EdgeInsets.symmetric(vertical: 14),
        child: Column(children: [
          Icon(icon, color: Colors.white),
          const SizedBox(height: 6),
          Text(label, textAlign: TextAlign.center, style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w600)),
        ]),
      ),
    ),
  );
}