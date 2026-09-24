import 'api_service.dart';
import 'local_store.dart';
import 'sync_service.dart';
import '../models/customer.dart';
import '../models/item_class.dart';
import '../models/load.dart';
import '../models/expense.dart';
import '../models/totals.dart';
import '../models/pickup_request.dart';

class DataService {
  final ApiService _api = ApiService();
  final SyncService syncService = SyncService();

  void init() => syncService.start();

  Future<List<Customer>> getCustomers() async {
    try {
      final data = await _api.getCustomers();
      LocalStore.saveCache('customers', data.map((c) => {'id': c.id, 'name': c.name, 'phone': c.phone}).toList());
      return data;
    } catch (_) {
      return LocalStore.readCache('customers').map((j) => Customer.fromJson(j)).toList();
    }
  }

  Future<Customer> createCustomer(String name, String? phone) => _api.createCustomer(name, phone);

  Future<List<ItemClass>> getItemClasses() async {
    try {
      final data = await _api.getItemClasses();
      LocalStore.saveCache('item_classes', data.map((c) => {
        'id': c.id, 'name': c.name, 'base_price': c.basePrice, 'unit_cost': c.unitCost, 'wash_minutes': c.washMinutes,
      }).toList());
      return data;
    } catch (_) {
      return LocalStore.readCache('item_classes').map((j) => ItemClass.fromJson(j)).toList();
    }
  }

  Future<List<Load>> getLoads(String start, String end) async {
    final key = 'loads_${start}_$end';
    try {
      final data = await _api.getLoads(start, end);
      LocalStore.saveCache(key, data.map(_loadToJson).toList());
      return data;
    } catch (_) {
      return LocalStore.readCache(key).map((j) => Load.fromJson(j)).toList();
    }
  }

  Future<List<Expense>> getExpenses(String start, String end) async {
    final key = 'expenses_${start}_$end';
    try {
      final data = await _api.getExpenses(start, end);
      LocalStore.saveCache(key, data.map(_expenseToJson).toList());
      return data;
    } catch (_) {
      return LocalStore.readCache(key).map((j) => Expense.fromJson(j)).toList();
    }
  }

  Future<Totals> getTotals(String start, String end) async {
    try {
      return await _api.getTotals(start, end);
    } catch (_) {
      final loads = LocalStore.readCache('loads_${start}_$end').map((j) => Load.fromJson(j)).toList();
      final expenses = LocalStore.readCache('expenses_${start}_$end').map((j) => Expense.fromJson(j)).toList();
      final sales = loads.fold<double>(0, (sum, l) => sum + l.total);
      final exp = expenses.fold<double>(0, (sum, e) => sum + e.amount);
      return Totals(sales: sales, expenses: exp, balance: sales - exp);
    }
  }

  Future<void> createLoad({
    required String customerName, String? customerPhone, required List<LoadItemInput> items, String? expectedPickupDate,
  }) async {
    final payload = {
      'customer_name': customerName, 'customer_phone': customerPhone,
      'items': items.map((i) => i.toJson()).toList(), 'expected_pickup_date': expectedPickupDate,
    };
    try {
      await _api.createLoad(customerName: customerName, customerPhone: customerPhone, items: items, expectedPickupDate: expectedPickupDate);
    } catch (_) {
      LocalStore.queueAction('createLoad', payload);
    }
  }

  Future<void> createExpense({required String category, required double amount, String? note}) async {
    try {
      await _api.createExpense(category: category, amount: amount, note: note);
    } catch (_) {
      LocalStore.queueAction('createExpense', {'category': category, 'amount': amount, 'note': note});
    }
  }

  Future<void> updateLoadStatus(int loadId, String status) async {
    try {
      await _api.updateLoadStatus(loadId, status);
    } catch (_) {
      LocalStore.queueAction('updateLoadStatus', {'load_id': loadId, 'status': status});
    }
  }

  Future<void> markLoadPaid(int loadId) async {
    try {
      await _api.markLoadPaid(loadId);
    } catch (_) {
      LocalStore.queueAction('markLoadPaid', {'load_id': loadId});
    }
  }

  Future<void> recordPayment(int loadId, double amount) async {
    try {
      await _api.recordPayment(loadId, amount);
    } catch (_) {
      LocalStore.queueAction('recordPayment', {'load_id': loadId, 'amount': amount});
    }
  }

  // Pickup requests: online-only for now, no offline queueing -- these are
  // lower-frequency, office-side actions rather than out-in-the-field ones.
  Future<List<PickupRequest>> getPickupRequests(String status) => _api.getPickupRequests(status);
  Future<PickupRequest> confirmPickupRequest(int id, String scheduledDate) => _api.confirmPickupRequest(id, scheduledDate);
  Future<Map<String, dynamic>> collectPickupRequest(int id, List<LoadItemInput> items, String? expectedPickupDate) =>
      _api.collectPickupRequest(id, items, expectedPickupDate);
  Future<void> cancelPickupRequest(int id) => _api.cancelPickupRequest(id);

  Future<Map<String, dynamic>> getSettings() => _api.getSettings();
  Future<Map<String, dynamic>> updateSettings(Map<String, dynamic> payload) => _api.updateSettings(payload);

  Map<String, dynamic> _loadToJson(Load l) => {
    'id': l.id, 'dropped_off_at': l.droppedOffAt, 'customer_id': l.customerId,
    'items': l.items.map((it) => {
      'id': it.id, 'item_class_id': it.itemClassId, 'quantity': it.quantity, 'price_charged': it.priceCharged, 'unit_cost': it.unitCost,
    }).toList(),
    'amount_paid': l.amountPaid, 'status': l.status, 'expected_pickup_date': l.expectedPickupDate, 'payment_status': l.paymentStatus,
    'delivery_method': l.deliveryMethod, 'pickup_address': l.pickupAddress, 'delivery_address': l.deliveryAddress,
  };

  Map<String, dynamic> _expenseToJson(Expense e) => {'id': e.id, 'date': e.date, 'category': e.category, 'amount': e.amount, 'note': e.note};
}