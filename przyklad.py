# coding=utf-8
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

# sprawdzam wersję zainstalowanej alchemi
print sqlalchemy.__version__

# definiujemy silnik bazy, jaki jest jak się logować i gdzie się znajduje
# echo oznacza, że do konsoli będą wypisywane zapytania które są generowane przez alchemię
# na razie nic się nie połączyło, tylko mówimy co i jak, na potem :)
engine = create_engine('mysql://root:root@localhost/nauka', echo=True)

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
insert = tabelka0.insert().values(kolumna_1='tekst')
print insert

# żeby zobaczyć rzeczywisty wynik zapytania
print insert.compile().params

# jednak jeszcze nic tak naprawdę nie zostało wstawione do bazy danych
# należy połączyć się z bazą, którą zdeklarowaliśmy
polaczenie = engine.connect()
print polaczenie

# chyba wypadało by też stworzyć tabelki które już zdefiniowaliśmy
metadata.create_all(engine)

# teraz można wykonać insera którego przygotowaliśmy i otrzymać wynik
wynik = polaczenie.execute(insert)

# UWAGA! podanie explicite wartości klucza głównego (nawet w przypadku auto incremetnt)
# powoduje że zostanie on użyty, co może powodować błędy integralności bazy
print wynik.inserted_primary_key

