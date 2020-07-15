import io
import re
import json
import logging

import requests
from django.core.exceptions import ObjectDoesNotExist, FieldError
from django.core.management import BaseCommand, call_command

from item.models import Color, Size, Season, Type, Brand, Item, Sku


def request_package_data(package_id, token):
    token = token.replace("\n", "")
    response = requests.post("https://www30.bhan.com.br:9443/api/v1/pacote/conteudo",
                             headers={'Authorization': 'Bearer {}'.format(token),
                                      'Content-Type': 'application/json'
                                      },
                             data=json.dumps({'cdPacote': package_id}))

    return json.loads(response.content)


def deactivate_package(package_id, token):
    token = token.replace("\n", "")
    response = requests.post("https://www30.bhan.com.br:9443/api/v1/pacote/envio",
                             headers={'Authorization': 'Bearer {}'.format(token),
                                      'Content-Type': 'application/json'
                                      },
                             data=json.dumps({'cdPacote': package_id}))

    return response


def generate_id(levels):
    id = list()
    for level in levels:
        id.append(level['cdGrupoNivel'])

    return " ".join(id)


class Command(BaseCommand):
    help = 'Get product data and insert to Item table'
    logger = logging.getLogger('item')

    def insert_color(self, colors):
        for color in colors:
            try:
                # Try get color object
                # If color object doesn't exist throw exception and insert this color
                Color.objects.get(id=color['cdCor'])
            except ObjectDoesNotExist:
                self.logger.info("Color {} id {} added".format(color["dsCor"], color['cdCor']))
                Color(id=color['cdCor'], name=color['dsCor']).save()

    def insert_size(self, sizes):
        for list_sizes in sizes:
            for size in list_sizes['itensGrade']:
                try:
                    # Try get size object
                    # If size object doesn't exist throw exception and insert this size
                    Size.objects.get(description=size['dsTamanho'])
                except ObjectDoesNotExist:
                    self.logger.info("Size {} added".format(size["dsTamanho"]))
                    Size(description=size['dsTamanho']).save()

    # Insert brands, types and collections
    def insert_specification(self, specs):
        for specification in specs:
            if specification['cdTipoclas'] == 111:
                for brand in specification['classificacoes']:
                    try:
                        Brand.objects.get(id=int(brand['cdClassificacao']))
                    except ObjectDoesNotExist:
                        self.logger.info(
                            "Brand {} id {} added".format(brand["dsClassificacao"], brand['cdClassificacao']))
                        Brand(id=int(brand['cdClassificacao']), name=brand['dsClassificacao']).save()
            if specification['cdTipoclas'] == 7:
                for season in specification['classificacoes']:
                    try:
                        Season.objects.get(id=int(season['cdClassificacao']))
                    except ObjectDoesNotExist:
                        self.logger.info(
                            "Season {} id {} added".format(season["dsClassificacao"], season['cdClassificacao']))
                        Season(id=int(season['cdClassificacao']), name=season['dsClassificacao']).save()
            if specification['cdTipoclas'] == 110:
                for item_type in specification['classificacoes']:
                    try:
                        Type.objects.get(id=int(item_type['cdClassificacao']))
                    except ObjectDoesNotExist:
                        self.logger.info(
                            "Type {} id {} added".format(item_type["dsClassificacao"], item_type['cdClassificacao']))
                        Type(id=int(item_type['cdClassificacao']), name=item_type['dsClassificacao']).save()

    # Insert sku
    # item is class Item instance
    def insert_sku(self, sku, item, additional_fields, specs):
        try:
            color = Color.objects.get(id=sku['cdCorSKU'])
            size = Size.objects.get(description=sku['dsTamanhoSKU'])

            item_sku = Sku(
                id=sku['nrProdutoSKU'],
                id_item=item,
                ean=sku['cdProdutoSKU'],
                color=color,
                size=size,
                weight=sku['qtPesoSKU']
            )

            for price in sku['valoresSKU']:
                if price['cdValorSKU'] == 10 and price['vlValorSKU'] != 0:
                    item.price = price['vlValorSKU']

            item_sku.save()
            item.save()

        except ObjectDoesNotExist:

            self.logger.error(
                "Sku {} wasn't inserted. Color id: {}, Size id: {}, Ean: {}, Weight: {}, Item id: {}".format(
                    sku['nrProdutoSKU'], sku['nrProdutoSKU'], sku['dsTamanhoSKU'], sku['cdProdutoSKU'],
                    sku['qtPesoSKU'], item.id))

    def get_specification(self, id, specs, item_specifications):
        for i in range(len(item_specifications)):
            if item_specifications[i]['cdTipoClasSKU'] == id:
                for j in range(len(specs)):
                    if specs[j]['cdTipoclas'] == id:
                        for specification in specs[j]['classificacoes']:
                            if specification['cdClassificacao'] == item_specifications[i]['cdClassificacaoSKU']:
                                return specification

    def get_additional_field(self, id, additional_fields, sku_additional_fields):
        for i in range(len(sku_additional_fields)):
            if sku_additional_fields[i]['cdCampoAdicSKU'] == id:
                for additional_field in additional_fields:
                    if additional_field['cdCampoAdic'] == id:
                        return {
                            'cdCampoAdic': additional_field['cdCampoAdic'],
                            'dsCampoAdic': additional_field['dsCampoAdic'],
                            'dsCampoAdicSKU': sku_additional_fields[i]['dsCampoAdicSKU']
                        }

    def handle(self, *args, **options):
        token = io.StringIO()
        packages = io.StringIO()

        call_command('gettoken', stdout=token)  # call command and get token value from console
        call_command('getpackages', stdout=packages)  # call command and get packages from console
        packages = eval(packages.getvalue())

        if 'pacotes' not in packages:
            self.logger.info("No packages available.")
        else:
            # Get package data from Virtual Age API using package_id
            for package_id in packages['pacotes']:
                # Passing package_id and token to request_package_data function to get package data
                data = request_package_data(package_id['cdPacote'], token.getvalue())

                # Checking if 'cores', 'grades' and 'tiposClassificacao' keys exist
                if 'cores' in data:
                    self.insert_color(data['cores'])
                if 'grades' in data:
                    self.insert_size(data['grades'])
                if 'tiposClassificacao' in data:
                    self.insert_specification(data['tiposClassificacao'])

                # Checking if 'referencias' key exist. This key has values from Items
                if 'referencias' in data:
                    regex = re.compile("^[0-9]{2} [0-9]{2} (0{2}[0-9]{4})")
                    for ref in data['referencias']:
                        item_id = generate_id(ref['niveis'])

                        try:
                            pattern = bool(regex.search(item_id))
                            if pattern:
                                item_genre = (self.get_specification(1, data['tiposClassificacao'],
                                                                     ref['SKUs'][0]['classificacoesSKU']))
                                item_type = (self.get_specification(110, data['tiposClassificacao'],
                                                                    ref['SKUs'][0]['classificacoesSKU']))
                                item_brand = (self.get_specification(111, data['tiposClassificacao'],
                                                                     ref['SKUs'][0]['classificacoesSKU']))
                                item_season = (self.get_specification(7, data['tiposClassificacao'],
                                                                      ref['SKUs'][0]['classificacoesSKU']))

                                try:
                                    if not item_season:
                                        raise FieldError("Season isn't valid. NULL")
                                    if not item_brand:
                                        raise FieldError("Brand isn't valid. NULL")
                                    if not item_type \
                                            or int(item_type['cdClassificacao']) == 41 \
                                            or int(item_type['cdClassificacao']) == 29 \
                                            or int(item_type['cdClassificacao']) == 30:
                                        raise FieldError(
                                            "Type isn't valid. NULL" if not item_type else "Type id {} not inserted".format(
                                                item_type['cdClassificacao']))
                                    else:
                                        item = Item(
                                            id=item_id,
                                            group=item_id.split(" ")[-1],
                                            genre=item_genre['dsClassificacao'] if item_genre else None,
                                            type=Type.objects.get(id=int(item_type['cdClassificacao'])),
                                            brand=Brand.objects.get(id=int(item_brand['cdClassificacao'])),
                                            season=Season.objects.get(id=int(item_season['cdClassificacao']))
                                        )

                                        item.save()

                                        for sku in ref['SKUs']:
                                            self.insert_sku(sku, item, data['camposAdicionais'],
                                                            data['tiposClassificacao'])

                                except ObjectDoesNotExist:
                                    self.logger.error(
                                        "Some field reference doesn't exist. Brand id: {}; Season id: {}; Type id: {}"
                                            .format(item_brand['cdClassificacao'], item_season['cdClassificacao'],
                                                    item_type['cdClassificacao']))
                                except FieldError as error:
                                    self.logger.info(error)
                            else:
                                raise FieldError(item_id)
                        except FieldError as error:
                            print("Item id {} isn't in pattern".format(error))

                response = deactivate_package(package_id['cdPacote'], token.getvalue())
                self.logger.info(
                    "Package validated. Http Status:{}".format(response.status_code))
