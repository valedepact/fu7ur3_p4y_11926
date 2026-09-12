import 'package:flutter/material.dart';

class PeriodTabs extends StatelessWidget {
  final String period;
  final ValueChanged<String> onChanged;

  const PeriodTabs({super.key, required this.period, required this.onChanged});

  static const _options = ['today', 'week', 'month'];

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      children: _options.map((p) {
        return ChoiceChip(
          label: Text(p),
          selected: period == p,
          onSelected: (_) => onChanged(p),
        );
      }).toList(),
    );
  }
}