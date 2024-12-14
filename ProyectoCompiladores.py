import sys
import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QLabel, QLineEdit, QPushButton, QComboBox, QGridLayout, QFrame
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import datetime
from lark import Lark, Transformer
from lark.tree import Tree

# Tasas de conversión de monedas actualizadas
conversion_rates = {
    "USD": {"EUR": 0.92, "JPY": 148.50, "GBP": 0.79, "CAD": 1.35, "USD": 1, "LPS": 24.73},
    "EUR": {"USD": 1.09, "JPY": 161.50, "GBP": 0.86, "CAD": 1.47, "EUR": 1, "LPS": 26.90},
    "JPY": {"USD": 0.0067, "EUR": 0.0062, "GBP": 0.0053, "CAD": 0.0091, "JPY": 1, "LPS": 0.17},
    "GBP": {"USD": 1.27, "EUR": 1.16, "JPY": 188.50, "CAD": 1.71, "GBP": 1, "LPS": 31.35},
    "CAD": {"USD": 0.74, "EUR": 0.68, "JPY": 110.37, "GBP": 0.58, "CAD": 1, "LPS": 18.33},
    "LPS": {"USD": 0.040, "EUR": 0.037, "JPY": 5.88, "GBP": 0.032, "CAD": 0.055, "LPS": 1}
}

# Gramática para la conversión de divisas
conversion_grammar = """
    ?start: AMOUNT CURRENCY "to" CURRENCY
          | AMOUNT CURRENCY "TO" CURRENCY
          | AMOUNT CURRENCY "a" CURRENCY
          | AMOUNT CURRENCY "A" CURRENCY

    AMOUNT: /[0-9]+(\.[0-9]+)?/
    CURRENCY: /[A-Za-z]{3}/

    %import common.WS_INLINE
    %ignore WS_INLINE
"""

class ConvertCurrency(Transformer):
    def start(self, items):
        """
        Transforma la entrada de conversión de moneda en un árbol sintáctico
        """
        amount = float(items[0])
        from_currency = items[1].upper()
        to_currency = items[2].upper()
        rate = conversion_rates[from_currency][to_currency]
        converted_amount = amount * rate
        tree = Tree('conversion', [Tree('amount', [amount]), Tree('from_currency', [from_currency]), Tree('to_currency', [to_currency]), Tree('converted_amount', [converted_amount])])
        return tree

# Crear el parser de conversión de monedas
conversion_parser = Lark(conversion_grammar, parser='lalr', transformer=ConvertCurrency())
convert_currency = conversion_parser.parse

class CurrencyChartApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Configuración de la ventana principal
        self.setWindowTitle('Convertidor de Divisas')
        self.setGeometry(100, 100, 1200, 800)

        # Estilo de interfaz en modo oscuro
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
                color: #E0E0E0;
            }
            QLabel {
                color: #E0E0E0;
                font-size: 16px;
            }
            QLineEdit, QComboBox {
                background-color: #1E1E1E;
                color: #E0E0E0;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2C3E50;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                transition: background-color 0.3s;
            }
            QPushButton:hover {
                background-color: #34495E;
                color: #FFFFFF;
            }
            QFrame {
                background-color: #1E1E1E;
                border-radius: 10px;
                padding: 15px;
            }
        """)

        # Widget central y diseño principal
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # Diseño horizontal para dos columnas
        main_layout = QHBoxLayout()
        
        # Columna izquierda - Sección de conversión
        left_column = QVBoxLayout()
        conversion_frame = QFrame()
        conversion_layout = QVBoxLayout(conversion_frame)
        
        # Sección de conversión de texto
        text_conversion_section = QFrame()
        text_conversion_layout = QVBoxLayout(text_conversion_section)
        text_conversion_layout.addWidget(QLabel('Conversión de Divisas (Entrada de Texto)'))
        
        self.input_lineedit = QLineEdit()
        self.input_lineedit.setPlaceholderText('Ejemplo: 10 USD a EUR')
        self.show_button = QPushButton('Convertir')
        self.result_label = QLabel()
        self.result_label.setWordWrap(True)
        self.show_button.clicked.connect(self.show_text)
        
        text_conversion_layout.addWidget(self.input_lineedit)
        text_conversion_layout.addWidget(self.show_button)
        text_conversion_layout.addWidget(self.result_label)
        
        # Sección de conversión con menús desplegables
        dropdown_conversion_section = QFrame()
        dropdown_conversion_layout = QGridLayout(dropdown_conversion_section)
        
        dropdown_conversion_layout.addWidget(QLabel('Monto:'), 0, 0)
        self.amount_input = QLineEdit()
        dropdown_conversion_layout.addWidget(self.amount_input, 0, 1)
        
        dropdown_conversion_layout.addWidget(QLabel('Moneda de Origen:'), 1, 0)
        self.from_currency_combo = QComboBox()
        self.from_currency_combo.addItems(conversion_rates.keys())
        dropdown_conversion_layout.addWidget(self.from_currency_combo, 1, 1)
        
        dropdown_conversion_layout.addWidget(QLabel('Moneda de Destino:'), 2, 0)
        self.to_currency_combo = QComboBox()
        self.to_currency_combo.addItems(conversion_rates.keys())
        dropdown_conversion_layout.addWidget(self.to_currency_combo, 2, 1)
        
        self.show_button_section2 = QPushButton('Convertir')
        self.show_button_section2.clicked.connect(self.show_text_section2)
        dropdown_conversion_layout.addWidget(self.show_button_section2, 3, 0, 1, 2)
        
        self.result_label_section2 = QLabel()
        dropdown_conversion_layout.addWidget(self.result_label_section2, 4, 0, 1, 2)
        
        # Agregar secciones de conversión a la columna izquierda
        conversion_layout.addWidget(text_conversion_section)
        conversion_layout.addWidget(dropdown_conversion_section)
        
        left_column.addWidget(conversion_frame)
        
        # Columna derecha - Sección de Gráfica
        right_column = QVBoxLayout()
        chart_frame = QFrame()
        chart_layout = QVBoxLayout(chart_frame)
        
        # Selección de divisas para la gráfica
        currency_selection_layout = QHBoxLayout()
        self.currency_label = QLabel('Moneda de Origen:')
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(['USD', 'EUR', 'JPY', 'GBP', 'CAD', 'LPS'])
        self.currency_combo.currentIndexChanged.connect(self.update_chart)
        
        self.to_currency_label_chart = QLabel('Moneda de Destino:')
        self.to_currency_combo_chart = QComboBox()
        self.to_currency_combo_chart.addItems(['USD', 'EUR', 'JPY', 'GBP', 'CAD', 'LPS'])
        self.to_currency_combo_chart.currentIndexChanged.connect(self.update_chart)
        
        currency_selection_layout.addWidget(self.currency_label)
        currency_selection_layout.addWidget(self.currency_combo)
        currency_selection_layout.addWidget(self.to_currency_label_chart)
        currency_selection_layout.addWidget(self.to_currency_combo_chart)
        
        # Lienzo de la gráfica
        self.chart_canvas = FigureCanvas(plt.figure(figsize=(8, 5), facecolor='#121212'))
        
        chart_layout.addLayout(currency_selection_layout)
        chart_layout.addWidget(self.chart_canvas)
        
        right_column.addWidget(chart_frame)
        
        # Agregar columnas al diseño principal
        main_layout.addLayout(left_column, 1)
        main_layout.addLayout(right_column, 1)
        
        self.central_widget.setLayout(main_layout)

        # Datos para la gráfica con fechas actualizadas
        self.dates = [
            datetime.date(2024, 1, 1),
            datetime.date(2024, 2, 1),
            datetime.date(2024, 3, 1),
            datetime.date(2024, 4, 1),
            datetime.date(2024, 5, 1),
            datetime.date(2024, 6, 1),
            datetime.date(2024, 7, 1),
            datetime.date(2024, 8, 1),
            datetime.date(2024, 9, 1),
            datetime.date(2024, 10, 1)
        ]

        # Valores de divisas de ejemplo (simulados)
        self.currency_values = {
            'USD': [1.0, 1.02, 1.05, 1.03, 1.01, 0.99, 1.04, 1.06, 1.02, 1.0],
            'EUR': [0.92, 0.93, 0.91, 0.90, 0.89, 0.88, 0.92, 0.94, 0.90, 0.92],
            'JPY': [148.50, 149.00, 147.75, 146.25, 148.00, 150.25, 149.50, 147.00, 148.75, 148.50],
            'GBP': [0.79, 0.80, 0.78, 0.77, 0.81, 0.82, 0.80, 0.79, 0.81, 0.79],
            'CAD': [1.35, 1.36, 1.34, 1.33, 1.37, 1.38, 1.35, 1.34, 1.36, 1.35],
            'LPS': [24.73, 24.80, 24.70, 24.65, 24.75, 24.85, 24.78, 24.72, 24.76, 24.73]
        }
        self.update_chart()

    def show_text(self):
        """
        Maneja la conversión de divisas por entrada de texto
        """
        input_text = self.input_lineedit.text()
        try:
            result = convert_currency(input_text)
            self.result_label.setText(f'Árbol Sintáctico:\n{result.pretty()}')
        except Exception as e:
            self.result_label.setText(f'Error al procesar la expresión: {e}')

    def show_text_section2(self):
        """
        Maneja la conversión de divisas por selección de menús desplegables
        """
        try:
            amount = float(self.amount_input.text())
            from_currency = self.from_currency_combo.currentText()
            to_currency = self.to_currency_combo.currentText()
            rate = conversion_rates[from_currency][to_currency]
            converted_amount = amount * rate
            self.result_label_section2.setText(f'Conversión: {amount} {from_currency} = {converted_amount:.2f} {to_currency}')
        except Exception as e:
            self.result_label_section2.setText(f'Error al procesar la expresión: {e}')

    def update_chart(self):
        """
        Actualiza la gráfica de tasas de cambio
        """
        selected_currency = self.currency_combo.currentText()
        to_currency = self.to_currency_combo_chart.currentText()

        rate = conversion_rates[selected_currency][to_currency]
        values = [rate * value for value in self.currency_values[selected_currency]]

        if values:
            self.chart_canvas.figure.clear()
            ax = self.chart_canvas.figure.add_subplot(1, 1, 1)
            
            # Estilo de gráfica en modo oscuro
            ax.set_facecolor('#121212')
            ax.plot(self.dates, values, marker='o', color='#4CAF50', linewidth=2)
            ax.set_xticks(self.dates)
            ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in self.dates], rotation=45, color='#E0E0E0')
            ax.set_xlabel('Fecha', color='#E0E0E0')
            ax.set_ylabel('Tasa de Cambio', color='#E0E0E0')
            ax.set_title(f'Tasa de Cambio: {selected_currency} a {to_currency}', color='#E0E0E0')
            
            # Colores de cuadrícula y ejes para modo oscuro
            ax.grid(True, color='#333333', linestyle='--', linewidth=0.5)
            ax.tick_params(colors='#E0E0E0')
            for spine in ax.spines.values():
                spine.set_edgecolor('#333333')

            plt.tight_layout()
            self.chart_canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = CurrencyChartApp()
    main_window.show()
    sys.exit(app.exec_())