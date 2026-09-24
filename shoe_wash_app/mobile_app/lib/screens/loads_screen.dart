import 'package:flutter/material.dart';

import '../services/data_service.dart';
import '../models/load.dart';
import '../models/customer.dart';
import '../models/item_class.dart';
import '../utils/labels.dart';
import '../theme.dart';
import 'load_detail_screen.dart';

const _statuses = ['dropped_off', 'washing', 'ready', 'picked_up', 'delivered'];

class LoadsScreen extends StatefulWidget {
  final DataService dataService;
  const LoadsScreen({super.key, required this.dataService});
  @override
  State<LoadsScreen> createState() => _LoadsScreenState();
}

class _LoadsScreenState extends State<LoadsScreen> {
  List<Load> _loads = [];
  List<Customer> _customers = [];
  List<ItemClass> _itemClasses = [];
  String _search = '';
  String _statusFilter = 'all';
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
      final loads = await widget.dataService.getLoads(iso(start), iso(end));
      final customers = await widget.dataService.getCustomers();
      final itemClasses = await widget.dataService.getItemClasses();
      setState(() { _loads = loads; _customers = customers; _itemClasses = itemClasses; _error = null; });
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  String _customerName(int id) => _customers.firstWhere((c) => c.id == id, orElse: () => Customer(id: id, name: '#$id')).name;
  String _customerPhone(int id) => _customers.firstWhere((c) => c.id == id, orElse: () => Customer(id: id, name: '')).phone ?? '';

  String _itemSummary(Load l) => l.items.map((it) =>
      '${it.quantity}x ${_itemClasses.firstWhere((c) => c.id == it.itemClassId, orElse: () => ItemClass(id: it.itemClassId, name: '#${it.itemClassId}', basePrice: 0)).name}'
  ).join(', ');

  @override
  Widget build(BuildContext context) {
    final visible = _loads.where((l) {
      final q = _search.toLowerCase();
      final matchesSearch = q.isEmpty || _customerName(l.customerId).toLowerCase().contains(q) || _customerPhone(l.customerId).toLowerCase().contains(q);
      final matchesStatus = _statusFilter == 'all' || l.status == _statusFilter;
      return matchesSearch && matchesStatus;
    }).toList()..sort((a, b) => b.droppedOffAt.compareTo(a.droppedOffAt));

    return Scaffold(
      appBar: AppBar(title: const Text('Loads')),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: Column(children: [
          Padding(padding: const EdgeInsets.all(12), child: TextField(
            decoration: const InputDecoration(prefixIcon: Icon(Icons.search), hintText: 'Search by name or phone...', border: OutlineInputBorder(), isDense: true),
            onChanged: (v) => setState(() => _search = v),
          )),
          SizedBox(height: 40, child: ListView(scrollDirection: Axis.horizontal, padding: const EdgeInsets.symmetric(horizontal: 12), children: [
            _FilterChip(label: 'All', selected: _statusFilter == 'all', onTap: () => setState(() => _statusFilter = 'all')),
            ..._statuses.map((s) => _FilterChip(label: statusLabels[s] ?? s, selected: _statusFilter == s, onTap: () => setState(() => _statusFilter = s))),
          ])),
          const SizedBox(height: 8),
          if (_error != null) Text(_error!, style: const TextStyle(color: AppColors.danger)),
          Expanded(child: ListView.builder(
            itemCount: visible.length,
            itemBuilder: (context, i) {
              final load = visible[i];
              return Card(margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4), child: ListTile(
                title: Text(_customerName(load.customerId)),
                subtitle: Text('${_customerPhone(load.customerId)}\n${_itemSummary(load)}'),
                isThreeLine: true,
                trailing: Column(mainAxisAlignment: MainAxisAlignment.center, crossAxisAlignment: CrossAxisAlignment.end, children: [
                  _Badge(text: statusLabels[load.status] ?? load.status, color: statusColor(load.status), bg: statusBg(load.status)),
                  const SizedBox(height: 4),
                  _Badge(text: paymentLabels[load.paymentStatus] ?? load.paymentStatus, color: paymentColor(load.paymentStatus), bg: paymentBg(load.paymentStatus)),
                ]),
                onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => LoadDetailScreen(dataService: widget.dataService, load: load))).then((_) => _refresh()),
              ));
            },
          )),
        ]),
      ),
    );
  }
}

class _FilterChip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;
  const _FilterChip({required this.label, required this.selected, required this.onTap});
  @override
  Widget build(BuildContext context) => Padding(padding: const EdgeInsets.only(right: 8), child: ChoiceChip(label: Text(label), selected: selected, onSelected: (_) => onTap()));
}

class _Badge extends StatelessWidget {
  final String text;
  final Color color, bg;
  const _Badge({required this.text, required this.color, required this.bg});
  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
    decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(999)),
    child: Text(text, style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w600)),
  );
}