import io
import json

import requests
from django.core.management import BaseCommand, call_command

from ...models import Item, Specs, Sku, Type, Brand, Collection, Genre


def join_duplicate_keys(ordered_pairs):
    d = {}
    for k, v in ordered_pairs:
        if k in d:
            if type(d[k]) == list:
                d[k].append(v)
            else:
                newlist = [d[k], v]
                d[k] = newlist
        else:
            d[k] = v
    return d


def get_package(id_package, token):
    header = {
        # 'Authorization': 'Bearer {}'.format(token),
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbnZpcm9ubWVudCI6ImJpYW1hciIsInNpZCI6IkJxbHZpVHhzeGNGK3haZWd5em9IaW1oSzJyWEd4VUE4Rm84OFlSWkhwaVk9IiwianRpIjoiZGJjODBmZGEtOGE3ZS00NTkzLTlmYWUtMTc1NTYxMTExYWRmIiwiZXhwIjoxNTg4MDc5MjkyLCJpc3MiOiJodHRwOi8vdmlydHVhbGFnZS5jb20uYnIifQ.Le0jdt4TAT8fJcMhKbm8BKgVQXmY-gSTDhce5THpT_Q',
        'Content-Type': 'application/json'
    }
    body = {
        "cdPacote": id_package,
    }

    response = requests.post("https://www30.bhan.com.br:9443/api/v1/pacote/conteudo", headers=header,
                             data=json.dumps(body))

    return json.loads(response.content, object_pairs_hook=join_duplicate_keys)


def add_color(id, colors):
    # Test if colors is dict, if true append to list
    if isinstance(colors, dict):
        aux = colors
        colors = [aux]

    for i in range(len(colors)):
        if id in colors[i]['cdCor']:
            return colors[i]['dsCor']


def add_specs(specs, package_specs, model_object):
    # specs is data[i]['SKU'][j]['classificacaoSKU']
    # package_especs is package['dados']['campoAdicional']
    # model_object is product.sku[j]

    def add_description(id, specs_description):
        # Test if sku_subclass is dict, if true append to list
        if isinstance(specs_description, dict):
            aux = specs_description
            specs_description = [aux]

        for i in range(len(specs_description)):
            if id == specs_description[i]['cdClassificacao']:
                return specs_description[i]['dsClassificacao']

    if isinstance(specs, dict):  # Test if sku_class is dict, if true append to list
        aux = specs
        specs = [aux]

    if isinstance(package_specs, dict):  # Test if package_type is dict, if true append to list
        aux = package_specs
        package_specs = [aux]

    for i in range(len(specs)):
        for j in range(len(package_specs)):
            if package_specs[j]['cdTipoclas'] != 6 and package_specs[j]['cdTipoclas'] != 112 and \
                    package_specs[j]['cdTipoclas'] != 7 and package_specs[j]['cdTipoclas'] != 1:

                if specs[i]['cdTipoClasSKU'] == package_specs[j]['cdTipoclas']:
                    model_object.specs.append(
                        Specs(id=specs[i]['cdTipoClasSKU'],
                              id_description=specs[i][
                                  'cdClassificacaoSKU'],
                              name=package_specs[j]['dsTipoclas'],
                              description=add_description(specs[i]['cdClassificacaoSKU'],
                                                          package_specs[j]['classificacao'])))

            # Add genre
            elif package_specs[j]['cdTipoclas'] == 1:
                if specs[i]['cdTipoClasSKU'] == package_specs[j]['cdTipoclas']:
                    model_object.genre.id = specs[i]['cdClassificacaoSKU']
                    model_object.genre.name = add_description(specs[i]['cdClassificacaoSKU'],
                                                              package_specs[j]['classificacao'])

            # Add brand
            elif package_specs[j]['cdTipoclas'] == 7:
                if specs[i]['cdTipoClasSKU'] == package_specs[j]['cdTipoclas']:
                    model_object.collection.id = specs[i]['cdClassificacaoSKU']
                    model_object.collection.season = add_description(specs[i]['cdClassificacaoSKU'],
                                                                     package_specs[j]['classificacao'])


def add_addicional_field(addicional_field, package_addicional_field, model_object):
    if isinstance(addicional_field, dict):  # Test if addicional_fields is dict, if true append to list
        aux = addicional_field
        addicional_field = [aux]

    if isinstance(package_addicional_field, dict):  # Test if pckg_addicional_fields is dict, if true append to list
        aux = package_addicional_field
        package_addicional_field = [aux]

    for i in range(len(addicional_field)):
        for j in range(len(package_addicional_field)):
            if addicional_field[i]['cdCampoAdicSKU'] == package_addicional_field[j]['cdCampoAdic']:
                model_object.additional_field.append(
                    Sku.AdditionalField(
                        id=addicional_field[i]['cdCampoAdicSKU'],
                        title=package_addicional_field[j]['dsCampoAdic'],
                        description=addicional_field[i]['dsCampoAdicSKU']))


class Command(BaseCommand):
    help = 'Deal with package and insert it'

    def handle(self, *args, **options):
        token = io.StringIO()
        packages = io.StringIO()

        call_command('getToken', stdout=token)  # call command and get token value from output
        call_command('getPackages', stdout=packages)  # call command and get packages from output

        # packages = json.loads(open("C:/Users/faguiar/Desktop/MongoDB/PacoteVA.json").read(),
        #                       object_pairs_hook=join_duplicate_keys)

        packages = eval(packages.getvalue())  # convert StringIO to dict
        # dirs = os.listdir('media/FOTOS')
        # dirs = os.listdir('media/FOTOS')
        errors = []

        if 'pacotes' not in packages:
            return "Nenhum pacote a ser inserido."
        else:
            for package_len in range(len(packages['pacotes'])):
                print("\nPACOTE", package_len)

                package = get_package(packages['pacotes'][package_len]['cdPacote'], token.getvalue().replace("\n", ""))
                data = package['dados']['referencia']

                if isinstance(data, dict):  # Test if data is dict, if true append to list
                    aux = data
                    data = [aux]

                for i in range(len(data)):
                    # Check if referencia isn't in pattern
                    if not (len(data[i]['cdRef'].split()) == 3 and len(data[i]['cdRef'].split()[2])) == 6:

                        if isinstance(data[i]['SKU'], dict):
                            aux = data[i]['SKU']
                            data[i]['SKU'] = [aux]

                        errors.append({"referencia": data[i]['cdRef'], "sku": data[i]['SKU'][0]['nrProdutoSKU']})

                    else:
                        # Check in db if referencia exist
                        if Item.objects.filter(id=data[i]['cdRef']).exists():
                            p = Item.objects.filter(id=data[i]['cdRef'])
                            p.delete()

                        # if not Photo.objects.filter(id=data[i]['cdRef'].split()[2]).exists():
                        #     photo = Photo(id=data[i]['cdRef'].split()[2])
                        #     for file in dirs:
                        #         if photo.id in file:
                        #             photo.front_photo.save(file, File(open('media/FOTOS/{}'.format(file), 'rb')))
                        #     photo.save()

                        # create a instance of model classes
                        product = Item()
                        product.brand = Brand()
                        product.genre = Genre()
                        product.type = Type()
                        product.collection = Collection()

                        # create a list of SKU and Classificacao model classes
                        product.sku = []
                        product.specs = []

                        product.id = data[i]['cdRef']
                        product.brand.id = data[i]['nivel'][1]['cdGrupoNivel']
                        product.brand.name = data[i]['nivel'][1]['dsGrupoNivel']
                        product.type.id = data[i]['nivel'][0]['cdGrupoNivel']
                        product.type.name = data[i]['nivel'][0]['dsGrupoNivel']

                        # Test if data['SKU'] is a dict, if true append to list
                        if isinstance(data[i]['SKU'], dict):
                            aux = data[i]['SKU']
                            data[i]['SKU'] = [aux]

                        for j in range(len(data[i]['SKU'])):

                            product.sku.append(Sku(id=data[i]['SKU'][j]['cdProdutoSKU'],
                                                   sku=data[i]['SKU'][j]['nrProdutoSKU'],
                                                   # id_cor=(data[i]['SKU'][j]['cdCorSKU']),
                                                   # cor=insert_color(data[i]['SKU'][j]['cdCorSKU'],
                                                   #                  package['dados']['cor']),
                                                   weight=data[i]['SKU'][j]['qtPesoSKU'],
                                                   size=data[i]['SKU'][j]['dsTamanhoSKU']))

                            product.sku[j].color = Sku.Color()
                            product.sku[j].color.id = data[i]['SKU'][j]['cdCorSKU']
                            product.sku[j].color.name = add_color(data[i]['SKU'][j]['cdCorSKU'],
                                                                  package['dados']['cor'])

                            if data[i]['SKU'][j]['valorSKU']['vlValorSKU'] != '0':
                                product.price = data[i]['SKU'][j]['valorSKU']['vlValorSKU']

                            # Test if values are None to avoid duplicated values in Classificacao model
                            if not product.collection.season and not product.specs:
                                add_specs(data[i]['SKU'][j]['classificacaoSKU'],
                                          package['dados']['tipoClassificacao'], product)

                            # Create a list of Campo Adicional model class
                            product.sku[j].additional_field = []

                            # Test if 'campoAdicional' and 'campoAdicSKU' keys exist in package and data,
                            # if true insert values in product.campo_adicional

                            if 'campoAdicional' in package['dados'] and 'campoAdicSKU' in data[i]['SKU'][j]:
                                add_addicional_field(data[i]['SKU'][j]['campoAdicSKU'],
                                                     package['dados']['campoAdicional'], product.sku[j])
                        # Save product instance
                        product.save()

                    print(data[i]['cdRef'])
            if errors:
                print("######## REFERÊNCIAS NÃO CADASTRADAS ########")
                for i in range(len(errors)):
                    print("Referência: ", errors[i]['referencia'], "SKU: ", errors[i]['sku'])
