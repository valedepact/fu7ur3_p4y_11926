import 'package:flutter/material.dart';

import '../services/data_service.dart';
import '../models/pickup_request.dart';
import '../theme.dart';
import 'pickup_request_confirm_screen.dart';

class PickupRequestsScreen extends StatefulWidget {
  final DataService dataService;
  const PickupRequestsScreen({super.key, required this.dataService});
  @override
  State<PickupRequestsScreen> createState() => _PickupRequestsScreenState();
}

class _PickupRequestsScreenState extends State<PickupRequestsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  List<PickupRequest> _requests = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _tabController.addListener(() { if (!_tabController.indexIsChanging) _refresh(); });
    _refresh();
  }

  Future<void> _refresh() async {
    final status = _tabController.index == 0 ? 'requested' : 'confirmed';
    try {
      final requests = await widget.dataService.getPickupRequests(status);
      setState(() { _requests = requests; _error = null; });
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Pickup Requests'), bottom: TabBar(controller: _tabController, tabs: const [Tab(text: 'Pending'), Tab(text: 'Confirmed')])),
      body: RefreshIndicator(onRefresh: _refresh, child: Column(children: [
        if (_error != null) Text(_error!, style: const TextStyle(color: AppColors.danger)),
        Expanded(child: ListView.builder(itemCount: _requests.length, itemBuilder: (context, i) {
          final r = _requests[i];
          return Card(margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4), child: ListTile(
            leading: const CircleAvatar(child: Icon(Icons.person)), title: Text(r.customerName), subtitle: Text('${r.phone}\n${r.address}'), isThreeLine: true,
            trailing: FilledButton(child: const Text('View'),
              onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => PickupRequestConfirmScreen(dataService: widget.dataService, request: r))).then((_) => _refresh())),
          ));
        })),
      ])),
    );
  }
}