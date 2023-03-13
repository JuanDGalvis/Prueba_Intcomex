from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

# clase para obtener una lista paginada de artículos de una categoría o subcategoría
class Articulos(Resource):
    def get(self, categoria, cantidad, pagina):
        # obtener la categoría o subcategoría de la base de datos
        categoria_db = Categoria.query.filter_by(nombre=categoria).first()
        subcategoria_db = Subcategoria.query.filter_by(nombre=categoria).first()
        if subcategoria_db:
            categoria_db = subcategoria_db.categoria # si se especifica una subcategoría, se obtiene su categoría padre
        if not categoria_db:
            return {"mensaje": "Categoría no encontrada"}, 404
        
        # obtener los artículos de la categoría o subcategoría, paginados
        articulos = Articulo.query.filter(Articulo.subcategoria_id.in_(c.id for c in categoria_db.subcategorias)).paginate(pagina, cantidad, False)
        if not articulos.items:
            return {"mensaje": "No hay artículos para mostrar"}, 404
        
        # construir la respuesta con los datos de los artículos
        response = {"articulos": []}
        for a in articulos.items:
            response["articulos"].append({
                "id_articulo": a.id_articulo,
                "sku": a.sku,
                "mpn": a.mpn,
                "nombre": a.nombre,
                "atributos": {}
            })
            for av in a.atributos:
                response["articulos"][-1]["atributos"][av.atributo.nombre] = av.valor
        
        # retornar la respuesta
        return response, 200

api.add_resource(Articulos, "/articulos/<string:categoria>/<int:cantidad>/<int:pagina>")

if __name__ == '__main__':
    app.run(debug=True)
