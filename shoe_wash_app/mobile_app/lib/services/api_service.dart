import 'dart:convert';
import 'package:http/http.dart' as http;

import '../config.dart';
import '../models/customer.dart';
import '../models/item_class.dart';
import '../models/load.dart';
import '../models/expense.dart';
import '../models/totals.dart';

class ApiService {
  Future<dynamic> _get(String path) async {
    final response = await http.get(Uri.parse('$apiBaseUrl$path'));
    if (response.statusCode >= 400) {
      throw Exception(jsonDecode(response.body)['detail'] ?? 'Request failed');
    }
    return jsonDecode(response.body);
  }

  Future<dynamic> _post(String path, Map<String, dynamic> body) async {
    final response = await http.post(
      Uri.parse('$apiBaseUrl$path'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(body),
    );
    if (response.statusCode >= 400) {
      throw Exception(jsonDecode(response.body)['detail'] ?? 'Request failed');
    }
    return jsonDecode(response.body);
  }

  Future<dynamic> _patch(String path, [Map<String, dynamic>? body]) async {
    final response = await http.patch(
      Uri.parse('$apiBaseUrl$path'),
      headers: {'Content-Type': 'application/json'},
      body: body != null ? jsonEncode(body) : null,
    );
    if (response.statusCode >= 400) {
      throw Exception(jsonDecode(response.body)['detail'] ?? 'Request failed');
    }
    return jsonDecode(response.body);
  }

  Future<List<Customer>> getCustomers() async {
    final data = await _get('/customers');
    return (data as List).map((e) => Customer.fromJson(e)).toList();
  }

  Future<List<ItemClass>> getItemClasses() async {
    final data = await _get('/item-classes');
    return (data as List).map((e) => ItemClass.fromJson(e)).toList();
  }

  Future<ItemClass> createItemClass(String name, double basePrice) async {
    final data = await _post('/item-classes', {'name': name, 'base_price': basePrice});
    return ItemClass.fromJson(data);
  }

  Future<List<Load>> getLoads(String start, String end) async {
    final data = await _get('/loads?start=$start&end=$end');
    return (data as List).map((e) => Load.fromJson(e)).toList();
  }

  Future<Load> createLoad({
    required String customerName,
    required int itemClassId,
    required int quantity,
    double? priceCharged,
    String? expectedPickupDate,
  }) async {
    final data = await _post('/loads', {
      'customer_name': customerName,
      'item_class_id': itemClassId,
      'quantity': quantity,
      'price_charged': priceCharged,
      'expected_pickup_date': expectedPickupDate,
    });
    return Load.fromJson(data);
  }

  Future<Load> updateLoadStatus(int loadId, String status) async {
    final data = await _patch('/loads/$loadId/status', {'status': status});
    return Load.fromJson(data);
  }

  Future<Load> markLoadPaid(int loadId) async {
    final data = await _patch('/loads/$loadId/pay');
    return Load.fromJson(data);
  }

  Future<List<Expense>> getExpenses(String start, String end) async {
    final data = await _get('/expenses?start=$start&end=$end');
    return (data as List).map((e) => Expense.fromJson(e)).toList();
  }

  Future<Expense> createExpense({
    required String category,
    required double amount,
    String? note,
  }) async {
    final data = await _post('/expenses', {'category': category, 'amount': amount, 'note': note});
    return Expense.fromJson(data);
  }

  Future<Totals> getTotals(String start, String end) async {
    final data = await _get('/totals?start=$start&end=$end');
    return Totals.fromJson(data);
  }
}