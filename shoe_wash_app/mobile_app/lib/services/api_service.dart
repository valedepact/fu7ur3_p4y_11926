import 'dart:convert';
import 'package:http/http.dart' as http;

import '../config.dart';
import '../models/customer.dart';
import '../models/item_class.dart';
import '../models/load.dart';
import '../models/expense.dart';
import '../models/totals.dart';
import '../models/pickup_request.dart';

class LoadItemInput {
  final int itemClassId;
  final int quantity;
  final double? priceCharged;

  LoadItemInput({required this.itemClassId, required this.quantity, this.priceCharged});

  Map<String, dynamic> toJson() => {'item_class_id': itemClassId, 'quantity': quantity, 'price_charged': priceCharged};
}

class ApiService {
  Future<dynamic> _get(String path) async {
    final response = await http.get(Uri.parse('$apiBaseUrl$path'));
    if (response.statusCode >= 400) throw Exception(jsonDecode(response.body)['detail'] ?? 'Request failed');
    return jsonDecode(response.body);
  }

  Future<dynamic> _post(String path, Map<String, dynamic> body) async {
    final response = await http.post(Uri.parse('$apiBaseUrl$path'), headers: {'Content-Type': 'application/json'}, body: jsonEncode(body));
    if (response.statusCode >= 400) throw Exception(jsonDecode(response.body)['detail'] ?? 'Request failed');
    return jsonDecode(response.body);
  }

  Future<dynamic> _patch(String path, [Map<String, dynamic>? body]) async {
    final response = await http.patch(Uri.parse('$apiBaseUrl$path'), headers: {'Content-Type': 'application/json'}, body: body != null ? jsonEncode(body) : null);
    if (response.statusCode >= 400) throw Exception(jsonDecode(response.body)['detail'] ?? 'Request failed');
    return jsonDecode(response.body);
  }

  Future<dynamic> _put(String path, Map<String, dynamic> body) async {
    final response = await http.put(Uri.parse('$apiBaseUrl$path'), headers: {'Content-Type': 'application/json'}, body: jsonEncode(body));
    if (response.statusCode >= 400) throw Exception(jsonDecode(response.body)['detail'] ?? 'Request failed');
    return jsonDecode(response.body);
  }

  Future<List<Customer>> getCustomers() async => (await _get('/customers') as List).map((e) => Customer.fromJson(e)).toList();

  Future<Customer> createCustomer(String name, String? phone) async =>
      Customer.fromJson(await _post('/customers', {'name': name, 'phone': phone, 'credit_limit': null}));

  Future<List<ItemClass>> getItemClasses() async => (await _get('/item-classes') as List).map((e) => ItemClass.fromJson(e)).toList();

  Future<List<Load>> getLoads(String start, String end) async =>
      (await _get('/loads?start=$start&end=$end') as List).map((e) => Load.fromJson(e)).toList();

  Future<Map<String, dynamic>> createLoad({
    required String customerName, String? customerPhone, required List<LoadItemInput> items, String? expectedPickupDate,
  }) async {
    final data = await _post('/loads', {
      'customer_name': customerName, 'customer_phone': customerPhone,
      'items': items.map((i) => i.toJson()).toList(), 'expected_pickup_date': expectedPickupDate,
    });
    return {'load': Load.fromJson(data['load']), 'warnings': List<String>.from(data['warnings'] ?? [])};
  }

  Future<Load> updateLoadStatus(int loadId, String status) async => Load.fromJson(await _patch('/loads/$loadId/status', {'status': status}));

  Future<Load> markLoadPaid(int loadId) async => Load.fromJson(await _patch('/loads/$loadId/pay'));

  Future<Load> recordPayment(int loadId, double amount) async => Load.fromJson(await _post('/loads/$loadId/payments', {'amount': amount}));

  Future<List<Expense>> getExpenses(String start, String end) async =>
      (await _get('/expenses?start=$start&end=$end') as List).map((e) => Expense.fromJson(e)).toList();

  Future<Expense> createExpense({required String category, required double amount, String? note, String? expenseDate}) async =>
      Expense.fromJson(await _post('/expenses', {'category': category, 'amount': amount, 'note': note, 'expense_date': expenseDate}));

  Future<Totals> getTotals(String start, String end) async => Totals.fromJson(await _get('/totals?start=$start&end=$end'));

  Future<List<PickupRequest>> getPickupRequests(String status) async =>
      (await _get('/pickup-requests?status=$status') as List).map((e) => PickupRequest.fromJson(e)).toList();

  Future<PickupRequest> confirmPickupRequest(int id, String scheduledDate) async =>
      PickupRequest.fromJson(await _patch('/pickup-requests/$id/confirm', {'scheduled_date': scheduledDate}));

  Future<Map<String, dynamic>> collectPickupRequest(int id, List<LoadItemInput> items, String? expectedPickupDate) async {
    final data = await _patch('/pickup-requests/$id/collect', {
      'items': items.map((i) => i.toJson()).toList(), 'expected_pickup_date': expectedPickupDate,
    });
    return {'load': Load.fromJson(data['load']), 'warnings': List<String>.from(data['warnings'] ?? [])};
  }

  Future<void> cancelPickupRequest(int id) async => await _patch('/pickup-requests/$id/cancel');

  Future<Map<String, dynamic>> getSettings() async => Map<String, dynamic>.from(await _get('/settings'));

  Future<Map<String, dynamic>> updateSettings(Map<String, dynamic> payload) async => Map<String, dynamic>.from(await _put('/settings', payload));
}