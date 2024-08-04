'''
CDMmodel.py is a representation of the Conceptual Data Models (CDM) in the form of a class template.
The class template is used in the CDMParser class to store the information extracted from the input CDM file (XML)
'''

# used for translating the datatype codes to human-readable form
datatypes = {
    "I": "Integer",
    "SI": "Short Integer",
    "LI": "Long Integer",
    "BT": "Byte",
    "N": "Number",
    "DC": "Decimal",
    "F": "Float",
    "SF": "Short Float",
    "LF": "Long Float",
    "MN": "Money",
    "NO": "Serial",
    "BL": "Boolean",
    "A": "Characters",
    "VA": "VARCHAR",
    "LA": "Long Characters",
    "LVA": "Long VARCHAR",
    "TXT": "Text",
    "MBT": "Multibyte",
    "VMBT": "Variable Multibyte",
    "D": "Date",
    "T": "Time",
    "DT": "Date and Time",
    "TS": "Timestamp",
    "BIN": "Binary",
    "LBIN": "Long Binary",
    "BMP": "Bitmap",
    "PIC": "Image",
    "OLE": "OLE Object",
    None: "Undefined"
}


class Model:
    def __init__(self, id, name, code, entities, inheritances, relationships, associations, association_links, domains,
                 packages=None):
        self.id = id
        self.name = name
        self.code = code
        self.entities: list[Entity] = entities
        self.relationships: list[Relationship] = relationships
        self.inheritances: list[Inheritance] = inheritances
        self.domains: list[Domain] = domains
        self.associations: list[Association] = associations
        self.association_links: list[AssociationLink] = association_links
        self.packages: list[Package] = packages if packages is not None else []

    def __str__(self):
        return (f"Model ({self.id}): {self.name}\n\t"
                f"Entities: {[entity.name for entity in self.entities]} \n\t"
                f"Inheritances: \n\t\t{'\n\t\t'.join([str(inheritance) for inheritance in self.inheritances])} \n\t"
                f"Relationships: \n\t\t{'\n\t\t'.join([str(relationship) for relationship in self.relationships])} \n\t"
                f"Associations: {[ass.name for ass in self.associations]}\n\t"
                f"Association links: \n\t\t{'\n\t\t'.join([str(link) for link in self.association_links])} \n\t"
                f"Domains: \n\t\t {'\n\t\t'.join([str(domain) for domain in self.domains])} \n\t"
                f"Packages: \n\t\t {'\n\t\t'.join([package.name for package in self.packages])}")

    def get_tables(self):
        return self.entities

    def get_table_name_by_id(self, table_id):
        for entity in self.entities:
            if entity.id == table_id:
                return entity.name
        return None

    def get_attributes(self, table_id):
        for entity in self.entities:
            if entity.id == table_id:
                return entity.attributes

    def get_identifiers(self, table_id):
        for entity in self.entities:
            if entity.id == table_id:
                return entity.identifiers


class Entity:
    def __init__(self, id, name, code, attributes, identifiers, relationships=None, links=None):
        self.id = id
        self.name = name
        self.code = code
        self.is_child = False
        self.attributes: list[Attribute] = attributes
        self.identifiers: list[Identifier] = identifiers
        self.relationships: list[Relationship] = relationships if relationships is not None else []
        self.association_links: list[AssociationLink] = links if links is not None else []

    def __str__(self):
        return (f"Entity({self.id}): {self.name} \n\t"
                f"Attributes: \n\t\t{'\n\t\t'.join([str(attribute) for attribute in self.attributes])}"
                f"\n\t Identifiers: \n\t\t{'\n\t\t'.join([str(identifier) for identifier in self.identifiers])}"
                f"\n\t Relationships: \n\t\t{'\n\t\t'.join([str(relationship) for relationship in self.relationships])}"
                f"\n\t Association links: \n\t\t{'\n\t\t'.join([str(link) for link in self.association_links])}")

    def puml(self, style_str):
        def resolve_primary_identifier_attributes(attribute):
            for ident in self.identifiers:
                if attribute in ident.identifier_attributes and ident.is_primary:
                    return True
            return False

        ret_str = f'entity "{self.name}" as {self.id} {style_str} ' + "{"
        for attribute in self.attributes:
            ret_str += f'\n\t* {attribute.name} : {datatypes[attribute.datatype]} {[attribute.length if attribute.length else ''][0]} {[attribute.precision if attribute.precision else ''][0]} {'MANDATORY' if attribute.mandatory else ''} {'PRIMARY KEY' if resolve_primary_identifier_attributes(attribute) else ''}'
        ret_str += " \n\t --"
        for identifier in self.identifiers:
            ret_str += f'\n\t* {identifier.name} {'PRIMARY KEY' if identifier.is_primary else ''}'

        ret_str += "\n}"

        return ret_str


class Attribute:
    def __init__(self, id, name, code, mandatory, domain, datatype, length=None, precision=None):
        self.id = id  # attributeID not dataItemID
        self.name = name
        self.code = code
        self.mandatory = mandatory
        self.datatype = datatype
        self.length = int(length) if length is not None else None
        self.precision = int(precision) if precision is not None else None
        self.domain: Domain = domain

def __str__(self):
    return f"Attribute({self.id}): {self.name} - {self.datatype}{(self.length, self.precision) if self.length else ''} {'-> IN DOMAIN: ' + self.domain.name + ' ' if self.domain else ''}- {"MANDATORY" if self.mandatory else "not mandatory"}"


class Identifier:
    def __init__(self, identifierID, identifier_name, identifier_attributes, primary_identifier):
        self.id = identifierID
        self.name = identifier_name
        self.identifier_attributes = identifier_attributes
        self.is_primary = primary_identifier

    def __str__(self):
        return f"Identifier({self.id}) {self.name} -> {''.join([str(attribute) for attribute in self.identifier_attributes])} - {"PRIMARY KEY" if self.is_primary else ''}"


class Relationship:
    def __init__(self, id, name, code, dependent_e1, dependent_e2, entity1, entity2, cardinality_1to2,
                 cardinality_2to1):
        self.id = id
        self.name = name
        self.code = code
        self.is_dependent_e1 = dependent_e1
        self.is_dependent_e2 = dependent_e2
        self.entity1: Entity = entity1
        self.entity2: Entity = entity2
        self.cardinality_1to2 = cardinality_1to2
        self.cardinality_2to1 = cardinality_2to1

    def __str__(self):
        return (
            f"Relationship({self.id}): {self.name} || {self.entity1.name} {" Dependent" if self.is_dependent_e1 else ""} ({self.cardinality_1to2}) {self.entity2.name} <--> {self.entity2.name}{" Dependent" if self.is_dependent_e2 else ""} ({self.cardinality_2to1}) {self.entity1.name}")

    def puml(self, style_str):
        # Dictionaries to map cardinality values to their visual representation in PlantUML
        cardinality21_visual = {
            '0,1': '|o',
            '1,1': '||',
            '1,n': '}|',
            '0,n': '}o',
        }
        cardinality12_visual = {
            '0,1': 'o|',
            '1,1': '||',
            '1,n': '|{',
            '0,n': 'o{',
        }

        # if the relationship is dependent, a dotted line is used to represent the dependency, otherwise straight
        # line is used
        if self.is_dependent_e1 or self.is_dependent_e2:
            line = '.'
        else:
            line = '-'

        ret_str = f'{self.entity2.id} {cardinality21_visual[self.cardinality_2to1]}{line}[{style_str}]{line}{cardinality12_visual[self.cardinality_1to2]} {self.entity1.id}: {self.name} \n'
        return ret_str


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


class Association:
    def __init__(self, id, name, code, attributes, links=None):
        self.id = id
        self.name = name
        self.code = code
        self.attributes: list[Attribute] = attributes
        self.association_links: list[AssociationLink] = links if links is not None else []

    def __str__(self):
        return (f"Association({self.id}): {self.name} \n\t"
                f"Attributes: \n\t\t{'\n\t\t'.join([str(attribute) for attribute in self.attributes])}"
                f"\n\t Association Links: \n\t\t{'\n\t\t'.join([str(association_link) for association_link in self.association_links])}")

    def puml(self, style_str):
        ret_str = f'entity "{self.name}" as {self.id} {style_str} ' + "{"
        for attribute in self.attributes:
            ret_str += f'\n\t* {attribute.name} : {datatypes[attribute.datatype]} {[attribute.length if attribute.length else ''][0]} {[attribute.precision if attribute.precision else ''][0]} {'MANDATORY' if attribute.mandatory else ''}'

        ret_str += "\n}"

        return ret_str


class AssociationLink:
    def __init__(self, id, association, entity, cardinality):
        self.id = id
        self.association: Association = association
        self.entity: Entity = entity
        self.cardinality = cardinality

    def __str__(self):
        return f"Association Link({self.id}): {self.entity.name} ({self.cardinality}) {self.association.name}"

    def puml(self, style_str):
        ret_str = f'{self.entity.id} "{self.cardinality}" -[{style_str}]- {self.association.id} \n'
        return ret_str


class Inheritance:
    def __init__(self, id, name, code, mutually_exclusive, complete, parent, children):
        self.id = id
        self.name = name
        self.code = code
        self.mutually_exclusive = mutually_exclusive
        self.complete = complete
        self.parent: Entity = parent
        self.children: list[Entity] = children

    def __str__(self):
        return (
            f"Inheritance({self.id}): {self.name}{" Mutually Exclusive " if self.mutually_exclusive else ""}{" COMPLETE" if self.complete else ""}\n\t"
            f"Parent: {self.parent.name} \n\t"
            f"Children: {[child.name for child in self.children]} \n\t")

    def puml(self, style_str_circle, style_str_line):
        ret_str_circle = f'circle "{self.name} {"Complete " if self.complete else ""}{"Mutually Exclusive " if self.mutually_exclusive else ""}" as {self.id} {style_str_circle}' + "\n"
        ret_str_lines = [f'{self.id} -[{style_str_line}]-|> {self.parent.id}']
        for child in self.children:
            ret_str_lines.append(f'{child.id} -[{style_str_line}]- {self.id}')
        return ret_str_circle, ret_str_lines


class Package(Model):
    def __init__(self, id, name, code, entities, inheritances, relationships, associations, association_links, domains,
                 packages=None):
        super().__init__(id, name, code, entities, inheritances, relationships, associations, association_links,
                         domains, packages)

    def __str__(self):
        return (f"Package ({self.id}): {self.name}\n\t"
                f"Entities: {[entity.name for entity in self.entities]} \n\t"
                f"Inheritances: \n\t\t{'\n\t\t'.join([str(inheritance) for inheritance in self.inheritances])} \n\t"
                f"Relationships: \n\t\t{'\n\t\t'.join([str(relationship) for relationship in self.relationships])} \n\t"
                f"Associations: {[ass.name for ass in self.associations]}\n\t"
                f"Association links: \n\t\t{'\n\t\t'.join([str(link) for link in self.association_links])} \n\t"
                f"Domains: \n\t\t {'\n\t\t'.join([str(domain) for domain in self.domains])}")

    def puml(self, style_str):
        ret_str = f'package "{self.name}" as {self.id} {style_str} ' + "{\n}"
        return ret_str
