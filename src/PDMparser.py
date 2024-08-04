import xml.etree.ElementTree as ET
import re
import PDMmodel



# add package support
class PDMParser:
    def __init__(self, path: str):
        self.path = path
        self.namespaces = {
            'a': 'attribute',
            'c': 'collection',
            'o': 'object',
        }
        self.tree = ET.parse(self.path)
        self.root = self.tree.getroot()

    def link_references(self, references: list[PDMmodel.Reference], tables: list[PDMmodel.Table], domains: list[PDMmodel.Domain]):
        for reference in references:
            reference.parent = [table for table in tables if reference.parent == table.id][0]
            reference.child = [table for table in tables if reference.child == table.id][0]

            for table in tables:
                for key in table.keys:
                    if reference.parent_key == key.id:
                        reference.parent_key = key

            reference.joins = [PDMmodel.Reference.ReferenceJoin(join.id, [column for column in reference.parent.columns if join.parent_column == column.id][0], [column for column in reference.child.columns if join.child_column == column.id][0]) for join in reference.joins]

    def link_keys(self, tables: list[PDMmodel.Table]):
            for table in tables:
                for key in table.keys:
                    key.columns = [column for column in table.columns if column.id in key.columns]
                    for column in key.columns:
                        column.in_key = True

    def link_domains(self, tables: list[PDMmodel.Table], domains: list[PDMmodel.Domain]):
        if domains is not None or len(domains) > 0:
            for table in tables:
                for column in table.columns:
                    if column.domain is not None:
                        column.domain = [domain for domain in domains if column.domain == domain.id][0]

    # must be called after link_keys
    def link_indexes(self, tables: list[PDMmodel.Table], references: list[PDMmodel.Reference]):
        for table in tables:
            for index in table.indexes:
                if index.key[0] == 'r':
                    index.key = [reference for reference in references if index.key[1:] == reference.id][0]
                else:
                    index.key = [key for key in table.keys if index.key[1:] == key.id][0]

                index.columns = [column for column in table.columns if column.id in index.columns]
                for column in index.columns:
                    column.in_index = True

    def resolve_key(self, key: ET.Element, primary_key_ref: str) -> PDMmodel.Key:
        def resolve_key_column(key: ET.Element) -> str:
            return key.attrib['Ref']

        id = key.attrib['Id']
        name = key.find("./a:Name", self.namespaces).text
        code = key.find("./a:Code", self.namespaces).text
        primary = id == primary_key_ref
        key_columns_ref = [resolve_key_column(key_column) for key_column in key.findall("./c:Key.Columns/", self.namespaces)]

        return PDMmodel.Key(id, name, code, primary, key_columns_ref)

    def resolve_index(self, index: ET.Element) -> PDMmodel.Index:
        def resolve_index_column(index: ET.Element) -> str:
            return index.find("./c:Column/o:Column", self.namespaces).attrib['Ref']

        id = index.attrib['Id']
        name = index.find("./a:Name", self.namespaces).text
        code = index.find("./a:Code", self.namespaces).text
        unique = index.find("./a:Unique", self.namespaces).text if index.find("./a:Unique", self.namespaces) is not None else None
        key_refs = index.findall("./c:LinkedObject/", self.namespaces)

        # k for key and r for reference <- used for link resolving
        for key_ref in key_refs:
            if key_ref.tag == "{object}Key":
                key_ref = "k" + key_ref.attrib['Ref']
            else:
                key_ref = "r" + key_ref.attrib['Ref']

        index_columns_refs = [resolve_index_column(index_column) for index_column in index.findall("./c:IndexColumns/", self.namespaces)]
        return PDMmodel.Index(id, name, code, unique, key_ref, index_columns_refs)

    def resolve_column(self, column: ET.Element) -> PDMmodel.Column:
        id = column.attrib['Id']
        name = column.find("./a:Name", self.namespaces).text
        code = column.find("./a:Code", self.namespaces).text
        mandatory = column.find("./a:Mandatory", self.namespaces).text
        datatype = datatype = re.sub("[(0-9)]|[(0-9,0-9)]", '', column.find("./a:DataType", self.namespaces).text)
        length = column.find("./a:Length", self.namespaces).text if column.find("./a:Length",
                                                                              self.namespaces) is not None else None
        precision = column.find("./a:Precision", self.namespaces).text if column.find("./a:Precision",
                                                                                  self.namespaces) is not None else None
        domain_ref = column.find("./c:Domain/o:PhysicalDomain", self.namespaces).attrib['Ref'] if column.find(
            "./c:Domain/o:PhysicalDomain", self.namespaces) is not None else None
        return PDMmodel.Column(id, name, code, mandatory,domain_ref, datatype, length, precision)

    def resolve_table(self, table: ET.Element) -> PDMmodel.Table:
        id = table.attrib['Id']
        name = table.find("./a:Name", self.namespaces).text
        code = table.find("./a:Code", self.namespaces).text

        columns = [self.resolve_column(column) for column in table.findall("./c:Columns/", self.namespaces)]
        primary_key_ref = table.find("./c:PrimaryKey/o:Key", self.namespaces).attrib['Ref']
        keys = [self.resolve_key(key, primary_key_ref) for key in table.findall("./c:Keys/", self.namespaces)]
        indexes = [self.resolve_index(index) for index in table.findall("./c:Indexes/", self.namespaces)]

        return PDMmodel.Table(id, name, code, columns, keys, indexes)

    def get_tables(self, model: ET.Element) -> list[PDMmodel.Table]:
        tables = model.findall("./c:Tables/", self.namespaces)
        return [self.resolve_table(table) for table in tables]

    def resolve_joins(self, joins: list[ET.Element]) -> list[PDMmodel.Reference.ReferenceJoin]:
        return_joins = []
        for join in joins:
            id = join.attrib['Id']
            parent_column_ref = join.find("./c:Object1/o:Column", self.namespaces).attrib['Ref']
            child_column_ref = join.find("./c:Object2/o:Column", self.namespaces).attrib['Ref']
            return_joins.append(PDMmodel.Reference.ReferenceJoin(id, parent_column_ref, child_column_ref))
        return return_joins

    def resolve_reference(self, reference: ET.Element) -> PDMmodel.Reference:
        id = reference.attrib['Id']
        name = reference.find("./a:Name", self.namespaces).text
        code = reference.find("./a:Code", self.namespaces).text
        cardinality = reference.find("./a:Cardinality", self.namespaces).text
        update_constraint = reference.find("./a:UpdateConstraint", self.namespaces).text
        delete_constraint = reference.find("./a:DeleteConstraint", self.namespaces).text
        parent_ref = reference.find("./c:ParentTable/o:Table", self.namespaces).attrib['Ref']
        child_ref = reference.find("./c:ChildTable/o:Table", self.namespaces).attrib['Ref']
        parent_key_ref = reference.find("./c:ParentKey/o:Key", self.namespaces).attrib['Ref']
        joins = self.resolve_joins(reference.findall("./c:Joins/", self.namespaces))
        return PDMmodel.Reference(id, name, code, cardinality, update_constraint, delete_constraint, parent_ref,
                                  parent_key_ref, child_ref, joins)

    def get_references(self, model: ET.Element) -> list[PDMmodel.Reference]:
        references = model.findall("./c:References/", self.namespaces)
        return [self.resolve_reference(reference) for reference in references]

    def resolve_domain(self, domain: ET.Element) -> PDMmodel.Domain:
        id = domain.attrib['Id']
        name = domain.find("./a:Name", self.namespaces).text
        code = domain.find("./a:Code", self.namespaces).text
        datatype = domain.find("./a:DataType", self.namespaces).text
        length = domain.find("./a:Length", self.namespaces).text if domain.find("./a:Length",
                                                                                self.namespaces) is not None else None
        precision = domain.find("./a:Precision", self.namespaces).text if domain.find("./a:Precision",
                                                                                      self.namespaces) is not None else None
        return PDMmodel.Domain(id, name, code, datatype, length, precision)

    def get_domains(self, model: ET.Element) -> list[PDMmodel.Domain]:
        domains = model.findall("./c:Domains/", self.namespaces)
        return [self.resolve_domain(domain) for domain in domains]

    def get_main_model(self) -> PDMmodel.Model:
        main_model = self.root.findall("./o:RootObject/c:Children/o:Model", self.namespaces)[0]
        id = main_model.attrib['Id']
        name = main_model.find("./a:Name", self.namespaces).text
        code = main_model.find("./a:Code", self.namespaces).text

        domains = self.get_domains(main_model)
        tables = self.get_tables(main_model)
        references = self.get_references(main_model)
        #packages = self.get_packages(main_model)

        self.link_references(references, tables, domains)
        self.link_domains(tables, domains)
        self.link_keys(tables)
        self.link_indexes(tables, references)

        return PDMmodel.Model(id, name, code, tables, references, domains)


if __name__ == '__main__':
    xml = PDMParser('W:/Diplomsko delo/Diploma/tests/domain_test.pdm')
    model = xml.get_main_model()
    print(model)
