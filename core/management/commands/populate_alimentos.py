from django.core.management.base import BaseCommand
from core.models import Alimento

class Command(BaseCommand):
    help = 'Popula o banco de dados com alimentos iniciais'

    def handle(self, *args, **kwargs):
        alimentos = [
            # Café da manhã
            {
                'nome': 'Pão Integral',
                'calorias': 247,
                'proteinas': 13,
                'gorduras': 3.4,
                'carboidratos': 41,
                'categoria': 'C',
                'porcao': 100
            },
            {
                'nome': 'Ovos',
                'calorias': 155,
                'proteinas': 13,
                'gorduras': 11,
                'carboidratos': 1.1,
                'categoria': 'C',
                'porcao': 100
            },
            {
                'nome': 'Iogurte Natural',
                'calorias': 59,
                'proteinas': 3.5,
                'gorduras': 3.3,
                'carboidratos': 4.7,
                'categoria': 'C',
                'porcao': 100
            },
            # Almoço
            {
                'nome': 'Arroz Integral',
                'calorias': 111,
                'proteinas': 2.6,
                'gorduras': 0.9,
                'carboidratos': 23,
                'categoria': 'A',
                'porcao': 100
            },
            {
                'nome': 'Feijão Preto',
                'calorias': 132,
                'proteinas': 8.9,
                'gorduras': 0.5,
                'carboidratos': 23.7,
                'categoria': 'A',
                'porcao': 100
            },
            {
                'nome': 'Peito de Frango',
                'calorias': 165,
                'proteinas': 31,
                'gorduras': 3.6,
                'carboidratos': 0,
                'categoria': 'A',
                'porcao': 100
            },
            # Jantar
            {
                'nome': 'Batata Doce',
                'calorias': 86,
                'proteinas': 1.6,
                'gorduras': 0.1,
                'carboidratos': 20.1,
                'categoria': 'J',
                'porcao': 100
            },
            {
                'nome': 'Salmão',
                'calorias': 208,
                'proteinas': 22,
                'gorduras': 13,
                'carboidratos': 0,
                'categoria': 'J',
                'porcao': 100
            },
            {
                'nome': 'Brócolis',
                'calorias': 55,
                'proteinas': 3.7,
                'gorduras': 0.6,
                'carboidratos': 11.2,
                'categoria': 'J',
                'porcao': 100
            },
            # Lanches
            {
                'nome': 'Banana',
                'calorias': 89,
                'proteinas': 1.1,
                'gorduras': 0.3,
                'carboidratos': 22.8,
                'categoria': 'L',
                'porcao': 100
            },
            {
                'nome': 'Castanha do Pará',
                'calorias': 656,
                'proteinas': 14.3,
                'gorduras': 67.1,
                'carboidratos': 11.7,
                'categoria': 'L',
                'porcao': 100
            },
            {
                'nome': 'Maçã',
                'calorias': 52,
                'proteinas': 0.3,
                'gorduras': 0.2,
                'carboidratos': 13.8,
                'categoria': 'L',
                'porcao': 100
            },
        ]

        for alimento_data in alimentos:
            Alimento.objects.get_or_create(
                nome=alimento_data['nome'],
                defaults=alimento_data
            )
            self.stdout.write(
                self.style.SUCCESS(f'Alimento "{alimento_data["nome"]}" criado com sucesso!')
            ) 