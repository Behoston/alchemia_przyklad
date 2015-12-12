# coding=utf-8
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql import and_, or_, not_

# sprawdzam wersję zainstalowanej alchemi
print 'wersja', sqlalchemy.__version__

# definiujemy silnik bazy, jaki jest jak się logować i gdzie się znajduje
# echo oznacza, że do konsoli będą wypisywane zapytania które są generowane przez alchemię
# na razie nic się nie połączyło, tylko mówimy co i jak, na potem :)
engine = create_engine('mysql://root:root@localhost/nauka?charset=utf8', echo=False)

# obiekt chyba reprezentuje bazę danych, można połączyć z instniejącą za pomocą Engine
# można skopiować wszystkie rzeczy z podanej bazy (reflect=True)
metadata = MetaData(bind=engine)

# klasa tabeli, tworzy się ją przede wszystkim podając nazwę i do której bazy (metadata) ma zostać przypisana
# kolejne argumenty to kolumny, każda ma swoją nazwę, typ i dodatkowe atrybuty takie jak ForeignKey, PrimaryKey, nullable
# niestety trzeba określić długość tekstu :/ miałem nadzieję że nie będzie trzeba...
tabelka0 = Table('tabelka0', metadata,
                 Column('ID', Integer, primary_key=True, autoincrement=True),
                 Column('kolumna_1', String(200), nullable=True))

# insert jest robiony do tabelki, można określić wartości i nie trzeba uzupełniać wszystkich kolumn
# oczywiśce jeśli nie są obowiązkowe
insert = tabelka0.insert().values(kolumna_1='tekst')
print 'pierwszy insert', insert

# żeby zobaczyć rzeczywisty wynik zapytania
print 'wartości inserta', insert.compile().params

# jednak jeszcze nic tak naprawdę nie zostało wstawione do bazy danych
# należy połączyć się z bazą, którą zdeklarowaliśmy
polaczenie = engine.connect()

# chyba wypadało by też stworzyć tabelki które już zdefiniowaliśmy
metadata.create_all(engine)

# teraz można wykonać insera którego przygotowaliśmy i otrzymać wynik
wynik = polaczenie.execute(insert)

# można każde zapytanie sobie wypisać jeśli się chce
print 'cały insert:', insert

# UWAGA! podanie explicite wartości klucza głównego (nawet w przypadku auto incremetnt)
# powoduje że zostanie on użyty, co może powodować błędy integralności bazy
print 'wstawiony klucz główny z autoincrement', wynik.inserted_primary_key

# można też wykonywać akcje bardziej generycznie
generyczny_insert = tabelka0.insert()
polaczenie.execute(generyczny_insert, kolumna_1='dziewiec')

# można też od razu wstawić wiele wierszy za jednym zamachem
# do tego celu należy użyć listy słowników
# UWAGA! każdy słownik musi zaiwerać te same klucze ponieważ
# polecenie SQL jest generowane na podstawie pierewszego elementu listy
polaczenie.execute(tabelka0.insert(), [
    {'kolumna_1': 'cos'},
    {'kolumna_1': 'cos drugiego'}
])
# można tego używać zarówno z insertami jak i updateami i deleteami

print '### Pobieranie danych z bazy'
from sqlalchemy.sql import select

s = select([tabelka0])
wynik = polaczenie.execute(s)
# to zwraca nam proxy do wyniku, najłatwiej jest przeiterować po wierszach
for row in wynik:
    print 'iterowanie:', row

# można też rzeczywiście pobrać całość wyniku
wynik = polaczenie.execute(s)
wszystkie_wyniki = wynik.fetchall()
print 'wszystkie:', wszystkie_wyniki

# lub pobierać je pojedynczo
wynik = polaczenie.execute(s)
jeden_wynik = wynik.fetchone()
while jeden_wynik:
    print 'pojedynczo:', jeden_wynik
    jeden_wynik = wynik.fetchone()

print '#### obsługa wiersza'
wynik = polaczenie.execute(s)
jeden_wynik = wynik.fetchone()
# każdy zwracany wiersz wygląda jak tupla, co podsuwa nam pomysł dostania się do danych poprzez indeks
print jeden_wynik[0], jeden_wynik[1]
# ale da się też dostać w sposób słownikowy
print jeden_wynik['ID'], jeden_wynik['kolumna_1']
# i na szczęście jest już zaimplementowane to czego mi brakowało po przeczytaniu powyższych dwóch metod
# można dostać się do wartości wiersza za pomocą kolumn, chociaż niestety IDE i tak nie podopowiada :/
print jeden_wynik[tabelka0.c.ID], jeden_wynik[tabelka0.c.kolumna_1]

print 'pobieranie tylko niektórych kolumn'
# dla przykładu odwróćmy sobie kolejność kolumn
s = select([tabelka0.c.kolumna_1, tabelka0.c.ID])
wynik = polaczenie.execute(s)
for row in wynik:
    print row

print 'filtrowanie wyników zapytania (WHERE)'
s = select([tabelka0]).where(tabelka0.c.ID == 10)
wynik = polaczenie.execute(s)
for row in wynik:
    print 'przefiltrowane:', row
# dodajmy sobie druga tabelkę i wybierzmy coś jak byłby tam klucz obcy
# definiujemy
tabelka1 = Table('tabelka1', metadata,
                 Column('ID', Integer, primary_key=True, autoincrement=True),
                 Column('slowo', String(200), nullable=True),
                 Column('tab0_ID', Integer))
# tworzymy
metadata.create_all(engine)
# wsytawiamy cokolwiek
polaczenie.execute(tabelka1.insert().values(slowo='slowo', tab0_ID=10))

# teraz możnemy wybrć coś z obydwu tabel, zaszaleję sobie i napiszę w jedenj linijce :E
print 'Niestety nie jest to ładny sposób prezentacji wyników, należało by usunąć wszelkie ID'
print polaczenie.execute(select([tabelka0, tabelka1]).where(tabelka0.c.ID == tabelka1.c.tab0_ID)).fetchall()

# tak wyglądać będą porównania
print 'Operatory porównywania'
print (tabelka0.c.ID <= tabelka1.c.tab0_ID)
print (tabelka0.c.ID == 7)
# ostatnie porównanie nie jest skompilowane, żeby rzeczywiście je obejrzeć trzeba napisać
print(tabelka0.c.ID == 7).compile().params
# działa większość Pythonowych operatorów, również operatory matematyczne (dodawania itd)
# można dodać też własny operator dla kolumny jeśli by coś nie działało ColumnOperators.op()
# TODO: nie rozumiem operatorów

## Operatory logiczne
print (and_(tabelka0.c.kolumna_1.like('j%'), or_(tabelka0.c.kolumna_1 == 'slowo', not_(tabelka0.c.kolumna_1 == 'cos'))))
# można też stosować pythonowe operatory logiczne, ale trzeba dostawiać nawiasy
print ((tabelka0.c.ID == 7) | (tabelka0.c.kolumna_1 == 'slowo'))
# można też wybierać wartości z zakresu, można też określić jak mają się nazywać kolumny po wybraniu ich z bazy
s = select([tabelka0.c.ID.label("identyfikator"), tabelka0.c.kolumna_1.label("kolumna pierwsza")]).where(tabelka0.c.ID.between(10, 15))

wynik = polaczenie.execute(s).fetchall()
print wynik
# jak widać label działa :)
print wynik[0]['identyfikator']

## Zapytania tekstowe
# SQL Alchemy oferuje również tekstowe zapytania, które z powodzeniem można parametryzować
# jest to użyteczne gdy potrzeba nam jakiejś funkcjonalności dosłownie na chwilę, lub nie potrafimy napisać zapytania
# używając SQL Alchemy (bo na przykład brak tej funkcjonalności)

