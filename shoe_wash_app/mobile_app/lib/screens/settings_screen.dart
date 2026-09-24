import 'package:flutter/material.dart';

import '../services/data_service.dart';
import '../theme.dart';

class SettingsScreen extends StatefulWidget {
  final DataService dataService;
  const SettingsScreen({super.key, required this.dataService});
  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _minutesController = TextEditingController();
  final _creditController = TextEditingController();
  final _abandonController = TextEditingController();
  bool _loaded = false;
  bool _saved = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    widget.dataService.getSettings().then((s) {
      _minutesController.text = s['daily_operating_minutes'].toString();
      _creditController.text = s['default_credit_limit'].toString();
      _abandonController.text = s['abandonment_days'].toString();
      setState(() => _loaded = true);
    }).catchError((e) => setState(() => _error = e.toString()));
  }

  Future<void> _save() async {
    try {
      await widget.dataService.updateSettings({
        'daily_operating_minutes': int.parse(_minutesController.text),
        'default_credit_limit': double.parse(_creditController.text),
        'abandonment_days': int.parse(_abandonController.text),
      });
      setState(() => _saved = true);
      Future.delayed(const Duration(seconds: 2), () { if (mounted) setState(() => _saved = false); });
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Business Settings')),
      body: !_loaded ? const Center(child: CircularProgressIndicator()) : ListView(padding: const EdgeInsets.all(16), children: [
        if (_error != null) Text(_error!, style: const TextStyle(color: AppColors.danger)),
        if (_saved) const Text('Saved.', style: TextStyle(color: AppColors.success)),
        const Text('Operating Minutes (per day)', style: TextStyle(fontWeight: FontWeight.bold)),
        TextField(controller: _minutesController, keyboardType: TextInputType.number, decoration: const InputDecoration(border: OutlineInputBorder())),
        const SizedBox(height: 16),
        const Text('Default Credit Limit per Customer (UGX)', style: TextStyle(fontWeight: FontWeight.bold)),
        TextField(controller: _creditController, keyboardType: TextInputType.number, decoration: const InputDecoration(border: OutlineInputBorder())),
        const SizedBox(height: 16),
        const Text('Abandoned-Item Threshold (days)', style: TextStyle(fontWeight: FontWeight.bold)),
        TextField(controller: _abandonController, keyboardType: TextInputType.number, decoration: const InputDecoration(border: OutlineInputBorder())),
        const SizedBox(height: 20),
        FilledButton(onPressed: _save, child: const Text('Save Changes')),
      ]),
    );
  }
}