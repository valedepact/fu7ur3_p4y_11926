import 'package:connectivity_plus/connectivity_plus.dart';

import 'api_service.dart';
import 'local_store.dart';

class SyncService {
  final ApiService _api = ApiService();
  bool _syncing = false;

  void start() {
    Connectivity().onConnectivityChanged.listen((result) {
      final online = !result.contains(ConnectivityResult.none);
      if (online) syncNow();
    });
    syncNow();
  }

  Future<void> syncNow() async {
    if (_syncing) return;
    _syncing = true;
    try {
      final pending = LocalStore.readPendingActions();
      for (final entry in pending.entries) {
        final action = entry.value['action'] as String;
        final payload = entry.value['payload'] as Map<String, dynamic>;
        try {
          await _replay(action, payload);
          LocalStore.removePendingAction(entry.key);
        } catch (_) {
          break; // still offline or server rejected -- stop, try again next time
        }
      }
    } finally {
      _syncing = false;
    }
  }

  Future<void> _replay(String action, Map<String, dynamic> payload) async {
    switch (action) {
      case 'createLoad':
        await _api.createLoad(
          customerName: payload['customer_name'],
          itemClassId: payload['item_class_id'],
          quantity: payload['quantity'],
          priceCharged: payload['price_charged']?.toDouble(),
          expectedPickupDate: payload['expected_pickup_date'],
        );
        break;
      case 'createExpense':
        await _api.createExpense(
          category: payload['category'],
          amount: (payload['amount'] as num).toDouble(),
          note: payload['note'],
        );
        break;
      case 'updateLoadStatus':
        await _api.updateLoadStatus(payload['load_id'], payload['status']);
        break;
      case 'markLoadPaid':
        await _api.markLoadPaid(payload['load_id']);
        break;
      case 'createItemClass':
        await _api.createItemClass(payload['name'], (payload['base_price'] as num).toDouble());
        break;
    }
  }
}