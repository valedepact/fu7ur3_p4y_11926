import 'api_service.dart';
import 'local_store.dart';
import 'sync_service.dart';
import '../models/customer.dart';
import '../models/item_class.dart';
import '../models/load.dart';
import '../models/expense.dart';
import '../models/totals.dart';

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

  Future<List<ItemClass>> getItemClasses() async {
    try {
      final data = await _api.getItemClasses();
      LocalStore.saveCache('item_classes', data.map((c) => {'id': c.id, 'name': c.name, 'base_price': c.basePrice}).toList());
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
    required String customerName,
    required int itemClassId,
    required int quantity,
    double? priceCharged,
    String? expectedPickupDate,
  }) async {
    final payload = {
      'customer_name': customerName, 'item_class_id': itemClassId, 'quantity': quantity,
      'price_charged': priceCharged, 'expected_pickup_date': expectedPickupDate,
    };
    try {
      await _api.createLoad(
        customerName: customerName, itemClassId: itemClassId, quantity: quantity,
        priceCharged: priceCharged, expectedPickupDate: expectedPickupDate,
      );
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

  Future<void> createItemClass(String name, double basePrice) async {
    try {
      await _api.createItemClass(name, basePrice);
    } catch (_) {
      LocalStore.queueAction('createItemClass', {'name': name, 'base_price': basePrice});
    }
  }

  Map<String, dynamic> _loadToJson(Load l) => {
    'id': l.id, 'dropped_off_at': l.droppedOffAt, 'customer_id': l.customerId, 'item_class_id': l.itemClassId,
    'quantity': l.quantity, 'price_charged': l.priceCharged, 'status': l.status,
    'expected_pickup_date': l.expectedPickupDate, 'payment_status': l.paymentStatus,
  };

  Map<String, dynamic> _expenseToJson(Expense e) =>
      {'id': e.id, 'date': e.date, 'category': e.category, 'amount': e.amount, 'note': e.note};
}