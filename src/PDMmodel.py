'''
The following is a representation of the Physical Data Models (PDM) in the form of a class template.
The class template is used in the PDMParser class to store the information extracted from the input PDM file (XML)
'''


class Model:
    def __init__(self, id, name, code, tables, references, domains, packages=None):
        self.id = id
        self.name = name
        self.code = code
        self.tables: list[Table] = tables
        self.references: list[Reference] = references
        self.domains: list[Domain] = domains
        self.packages: list[Package] = packages if packages is not None else []

    def __str__(self):
        return (f"Model ({self.id}): {self.name}\n\t"
                f"Entities: {[table.name for table in self.tables]} \n\t"
                f"References: \n\t\t{'\n\t\t'.join([reference.name + ' ('+ reference.id + ')' for reference in self.references])} \n\t"
                f"Domains: \n\t\t {'\n\t\t'.join([str(domain) for domain in self.domains])} \n\t"
                f"Packages: \n\t\t {'\n\t\t'.join([package.name for package in self.packages])}")


class Table:
    def __init__(self, id, name, code, columns, keys=None, indexes=None):
        self.id = id
        self.name = name
        self.code = code

        self.columns: list[Column] = columns
        self.keys: list[Key] = keys if keys is not None else []
        self.indexes: list[Index] = indexes if indexes is not None else []

    def __str__(self):
        return f"Table({self.id}): {self.name} \n COLUMNS: {[column.name for column in self.columns]} \n KEYS: {[key.name for key in self.keys]} \n INDEXES: {[index.name for index in self.indexes]}"


class Column:
    def __init__(self, id, name, code, mandatory, domain, datatype, length=None, precision=None):
        self.id = id  # attributeID not dataItemID
        self.name = name
        self.code = code
        self.mandatory = mandatory
        self.in_key: Key = None
        self.in_index: Index = None
        self.datatype = datatype
        self.length = int(length) if length is not None else None
        self.precision = int(precision) if precision is not None else None
        self.domain: Domain = domain

    def __str__(self):
        return f"Column({self.id}): {self.name} - {self.datatype}{(self.length, self.precision) if self.length else ''} {('-> IN DOMAIN: ' + self.domain.name + ' ') if self.domain else ''}- {"MANDATORY" if self.mandatory else "not mandatory"}{" - IN KEY" if self.in_key else ""}{" - IN INDEX" if self.in_index else ""}"


class Key:
    def __init__(self, id, name, code, primary, columns):
        self.id = id
        self.name = name
        self.code = code
        self.primary = primary
        self.columns: list[Column] = columns
    def __str__(self):
        return f"Key({self.id}): {self.name}, {"PRIMARY KEY" if self.primary else ''} \n KEY COLUMNS:{[column.name for column in self.columns]}"


class Index:
    def __init__(self, id, name, code, unique, key, columns):
        self.id = id
        self.name = name
        self.code = code
        self.unique = unique
        self.key: Key | Reference = key
        self.columns: list[Column] = columns

    def __str__(self):
        return f"Index({self.id}): {self.name}, INDEX KEY:{self.key} \n INDEX COLUMNS:{[column.name for column in self.columns]}"


# add update, delete constraint dictionary
class Reference:
    def __init__(self, id, name, code, cardinality, update_constraint, delete_constraint, parent, parent_key, child,
                 joins=None):
        self.id = id
        self.name = name
        self.code = code
        self.cardinality = cardinality
        self.update_constraint = update_constraint
        self.delete_constraint = delete_constraint
        self.parent: Table = parent
        self.parent_key: Key = parent_key
        self.child: Table = child
        self.joins: list[Reference.ReferenceJoin] = joins if joins is not None else []

    def __str__(self):
        return f"Reference({self.id}): {self.name} || {self.parent.name} ({self.cardinality}) {self.child.name} {[str(join) for join in self.joins]} {self.update_constraint} {self.delete_constraint}"

    class ReferenceJoin:
        def __init__(self, id, parent, child):
            self.id = id
            self.parent_column: Column = parent
            self.child_column: Column = child

        def __str__(self):
            return f"ReferenceJoin({self.id}): {self.parent_column.name} -> {self.child_column.name}"


class Domain:
    def __init__(self, id, name, code, datatype, length, precision):
        self.id = id
        self.name = name
        self.code = code
        self.datatype = datatype
        self.length = int(length) if length is not None else None
        self.precision = int(precision) if precision is not None else None

    def __str__(self):
        return f"Domain({self.id}): {self.name} - {self.datatype} {(self.length, self.precision) if self.length else ''}"


class Package(Model):
    def __init__(self, id, name, code, tables, references, domains, packages):
        super().__init__(id, name, code, tables, references, domains, packages)

    def __str__(self):
        return (f"Package ({self.id}): {self.name}\n\t"
                f"Entities: {[table.name for table in self.tables]} \n\t"
                f"References: \n\t\t{'\n\t\t'.join([reference.name + ' (' + reference.id + ')' for reference in self.references])} \n\t"
                f"Domains: \n\t\t {'\n\t\t'.join([str(domain) for domain in self.domains])} \n\t"
                f"Packages: \n\t\t {'\n\t\t'.join([package.name for package in self.packages])}")
