import 'package:flutter/material.dart';

import 'screens/overview_screen.dart';
import 'screens/loads_screen.dart';
import 'screens/expenses_screen.dart';
import 'screens/customers_screen.dart';
import 'screens/item_classes_screen.dart';
import 'services/local_store.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await LocalStore.init();
  runApp(const ShoeWashApp());
}

class ShoeWashApp extends StatelessWidget {
  const ShoeWashApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Shoe Wash',
      theme: ThemeData(useMaterial3: true, colorSchemeSeed: const Color(0xFF2E6F77)),
      home: const HomeShell(),
    );
  }
}

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int _index = 0;

  final _screens = const [
    OverviewScreen(),
    LoadsScreen(),
    ExpensesScreen(),
    CustomersScreen(),
    ItemClassesScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.dashboard), label: 'Overview'),
          NavigationDestination(icon: Icon(Icons.local_laundry_service), label: 'Sales'),
          NavigationDestination(icon: Icon(Icons.receipt_long), label: 'Expenses'),
          NavigationDestination(icon: Icon(Icons.people), label: 'Customers'),
          NavigationDestination(icon: Icon(Icons.category), label: 'Services'),
        ],
      ),
    );
  }
}