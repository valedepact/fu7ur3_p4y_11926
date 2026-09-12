import 'dart:convert';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:uuid/uuid.dart';

class LocalStore {
  static const _pendingBox = 'pending_actions';
  static const _cacheBox = 'cache';
  static final _uuid = const Uuid();

  static Future<void> init() async {
    await Hive.initFlutter();
    await Hive.openBox<String>(_pendingBox);
    await Hive.openBox<String>(_cacheBox);
  }

  static void saveCache(String key, List<Map<String, dynamic>> items) {
    Hive.box<String>(_cacheBox).put(key, jsonEncode(items));
  }

  static List<Map<String, dynamic>> readCache(String key) {
    final raw = Hive.box<String>(_cacheBox).get(key);
    if (raw == null) return [];
    return (jsonDecode(raw) as List).cast<Map<String, dynamic>>();
  }

  static void queueAction(String action, Map<String, dynamic> payload) {
    final id = _uuid.v4();
    Hive.box<String>(_pendingBox).put(id, jsonEncode({'action': action, 'payload': payload}));
  }

  static Map<String, Map<String, dynamic>> readPendingActions() {
    final box = Hive.box<String>(_pendingBox);
    return {
      for (final key in box.keys) key.toString(): jsonDecode(box.get(key)!) as Map<String, dynamic>,
    };
  }

  static void removePendingAction(String id) => Hive.box<String>(_pendingBox).delete(id);

  static int get pendingCount => Hive.box<String>(_pendingBox).length;
}