<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS><TS version="2.0" language="fr_FR" sourcelanguage="">
<context>
    <name>InMaskFunction</name>
    <message>
        <location filename="../aeag_mask.py" line="120"/>
        <source>&lt;h1&gt;in_mask function&lt;/h1&gt;
Expression function added by mask plugin. Returns true if current feature
crosses mask geometry.&lt;br/&gt;
The spatial expression to use is set from the mask UI button (exact, fast
using centroids, intermediate using point on surface).&lt;br/&gt;
in_mask takes a CRS EPSG code as first parameter, which is the CRS code of the
evaluated features.&lt;br/&gt;
It can be used to filter labels only in that area, or since QGIS 2.13, legend
items only visible in mask area.&lt;br/&gt;
&lt;h2&gt;Return value&lt;/h2&gt;
true/false (0/1)&lt;br/&gt;
&lt;h2&gt;Usage&lt;/h2&gt;
in_mask(2154)</source>
        <translation>&lt;h1&gt;Fonction in_mask&lt;/h1&gt;
Fonction ajoutée par le plugin Mask. Renvoie vrai si l&apos;entité courante intersecte la géométrie de masque.&lt;br/&gt;
Les options de l&apos;intersection spatiale (exacte, utilisant les centroïdes ou un point sur la surface, etc.) peuvent être réglées par la boite de dialogue de configuration du plugin Mask.&lt;br/&gt;
in_mask prend un code EPSG de projection en premier paramètre qui représente la projection de l&apos;entité courante.&lt;br/&gt;
Cette fonction peut être utilisée pour filtrer des étiquettes ou, à partir de QGIS 2.13, pour filtrer des élements de légende.&lt;br/&gt;
&lt;h2&gt;Valeur retournée&lt;/h2&gt;
vrai/faux (0/1)&lt;br/&gt;
&lt;h2&gt;Utilisation&lt;/h2&gt;
in_mask(2154)</translation>
    </message>
</context>
<context>
    <name>LayerListWidget</name>
    <message>
        <location filename="../ui/ui_layer_list.ui" line="36"/>
        <source>Exact (slow and will disable simplification)</source>
        <translation>Exacte (lente et désactivera la simplification)</translation>
    </message>
    <message>
        <location filename="../ui/ui_layer_list.ui" line="84"/>
        <source>Limit</source>
        <translation>Limiter</translation>
    </message>
    <message>
        <location filename="../ui/ui_layer_list.ui" line="89"/>
        <source>Layer</source>
        <translation>Couche</translation>
    </message>
    <message>
        <location filename="../ui/ui_layer_list.ui" line="14"/>
        <source>Form</source>
        <translation>Formulaire</translation>
    </message>
    <message>
        <location filename="../ui/ui_layer_list.ui" line="25"/>
        <source>Function used for labeling filtering on polygons</source>
        <translation>Fonction utilisée pour filtrer les étiquettes des polygones</translation>
    </message>
    <message>
        <location filename="../ui/ui_layer_list.ui" line="41"/>
        <source>The mask geometry contains the centroid</source>
        <translation>Le masque contient le centroïde</translation>
    </message>
    <message>
        <location filename="../ui/ui_layer_list.ui" line="46"/>
        <source>The mask geometry contains a point on the polygon surface</source>
        <translation>Le masque contient un point de la surface</translation>
    </message>
    <message>
        <location filename="../ui/ui_layer_list.ui" line="54"/>
        <source>Function used for labeling filtering on lines</source>
        <translation>Fonction utilisée pour filtrer les étiquettes des lignes</translation>
    </message>
    <message>
        <location filename="../ui/ui_layer_list.ui" line="65"/>
        <source>The mask geometry intersects the line</source>
        <translation>Le masque intersecte la ligne</translation>
    </message>
    <message>
        <location filename="../ui/ui_layer_list.ui" line="70"/>
        <source>The mask geometry contains the line</source>
        <translation>Le masque contient la ligne</translation>
    </message>
    <message>
        <location filename="../ui/ui_layer_list.ui" line="99"/>
        <source>Select all</source>
        <translation>Sélectionner tout</translation>
    </message>
    <message>
        <location filename="../ui/ui_layer_list.ui" line="106"/>
        <source>Unselect all</source>
        <translation>Désélectionner tout</translation>
    </message>
</context>
<context>
    <name>MainDialog</name>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="14"/>
        <source>Define a mask</source>
        <translation>Définir un masque</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="57"/>
        <source>Edit</source>
        <translation>Editer</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="83"/>
        <source>Buffer</source>
        <translation>Tampon</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="106"/>
        <source>Units</source>
        <translation>Unités</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="129"/>
        <source>Segments</source>
        <translation>Segments</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="157"/>
        <source>On-the-fly simplification</source>
        <translation>Simplification à la volée</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="177"/>
        <source>Tolerance</source>
        <translation>Tolérance</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="197"/>
        <source>pixels</source>
        <translation>pixels</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="212"/>
        <source>Limit labeling to mask&apos;s polygon</source>
        <translation>Limiter l&apos;étiquettage au polygone de masque</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="229"/>
        <source>Save as</source>
        <translation>Sauvegarder sous</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="246"/>
        <source>...</source>
        <translation>...</translation>
    </message>
    <message>
        <location filename="../ui/maindialog.py" line="71"/>
        <source>Save as defaults</source>
        <translation>Sauver comme valeurs par défaut</translation>
    </message>
    <message>
        <location filename="../ui/maindialog.py" line="79"/>
        <source>Load defaults</source>
        <translation>Charger les valeurs par défaut</translation>
    </message>
    <message>
        <location filename="../ui/maindialog.py" line="365"/>
        <source>Warning</source>
        <translation>Attention</translation>
    </message>
    <message>
        <location filename="../ui/maindialog.py" line="106"/>
        <source>Create a mask</source>
        <translation>Créer un masque</translation>
    </message>
    <message>
        <location filename="../ui/maindialog.py" line="108"/>
        <source>Update the current mask</source>
        <translation>Mettre à jour le masque existant</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="23"/>
        <source>Style</source>
        <translation>Style</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="142"/>
        <source>5</source>
        <translation>5</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="190"/>
        <source>1.0</source>
        <translation>1.0</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="20"/>
        <source>Style to use for mask layer</source>
        <translation>Style à utiliser pour la couche de masque</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="80"/>
        <source>Buffer around the mask geometry</source>
        <translation>Tampon autour de la géométrie de masque</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="154"/>
        <source>On-the-fly simplification used for the mask geometry used in expressions ($mask_geometry)</source>
        <translation>Simplification à la volée utilisée pour la géométrie de masque dans les expressions ($mask_geometry)</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="209"/>
        <source>If a layer is checked here, its labeling options will be modified in order that its labels will be only visible from inside the mask&apos;s polygon</source>
        <translation>Si une couche est sélectionnée ici, ses options d&apos;étiquetage seront modifiées pour que les étiquettes ne soient visibles qu&apos;à l&apos;intérieur du polygone de masque</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="226"/>
        <source>Whether the save the mask layer. By default a memory layer is created</source>
        <translation>Est-ce que la couche de masque doit être sauvegardée. Par défaut une couche mémoire est créée.</translation>
    </message>
    <message>
        <location filename="../ui/maindialog.py" line="238"/>
        <source>Select a filename to save the mask layer to</source>
        <translation>Sélectionnez un nom de fichier pour sauvegarder la couche de masque</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="253"/>
        <source>&apos;&apos;</source>
        <translation>&apos;&apos;</translation>
    </message>
    <message>
        <location filename="../ui/maindialog.py" line="365"/>
        <source>Some layer have rendering simplification turned on,                     which is not compatible with the labeling filtering you choose.                     Force simplification disabling ?</source>
        <translation>La simplification à la volée est activée sur certaines couches, ce qui n&apos;est pas compatible avec la méthode de filtrage des étiquettes choisie. Désactiver la simplification à la volée sur ces couches ?</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="265"/>
        <source>Interacts with Atlas (layout)</source>
        <translation>Interagit avec l&apos;atlas (cf. mises en page)</translation>
    </message>
    <message>
        <location filename="../ui/ui_plugin_mask.ui" line="274"/>
        <source>The mask will automatically be applied to Atlas (by default)</source>
        <translation>Par défaut, le masque sera appliqué à la couche de couverture de l&apos;atlas</translation>
    </message>
</context>
<context>
    <name>MaskGeometryFunction</name>
    <message>
        <location filename="../aeag_mask.py" line="93"/>
        <source>&lt;h1&gt;$mask_geometry&lt;/h1&gt;
Variable filled by mask plugin.&lt;br/&gt;
When mask has been triggered on some polygon, mask_geometry is filled with the
mask geometry and can be reused for expression/python calculation. in_mask
variable uses that geometry to compute a boolean.
&lt;h2&gt;Return value&lt;/h2&gt;
The geometry of the current mask
        </source>
        <translation>&lt;h1&gt;$mask_geometry&lt;/h1&gt;
Variable renseignée par le plugin Mask.&lt;br/&gt;
Quand le mask a été créé sur un polygone, la variable $mask_geometry représente la géométrie de ce polygone et peut être réutilisée dans une expression. La fonction in_mask() utilise cette géométrie pour son calcul.
&lt;h2&gt;Valeur de retour&lt;/h2&gt;
La géométrie courante du masque</translation>
    </message>
</context>
<context>
    <name>aeag_mask</name>
    <message>
        <location filename="../aeag_mask.py" line="858"/>
        <source>Mask plugin error</source>
        <translation>Erreur du plugin Mask</translation>
    </message>
    <message>
        <location filename="../aeag_mask.py" line="679"/>
        <source>No polygon selection !</source>
        <translation>Aucune sélection !</translation>
    </message>
    <message>
        <location filename="../aeag_mask.py" line="722"/>
        <source>Create a mask</source>
        <translation>Créer un masque</translation>
    </message>
    <message>
        <location filename="../aeag_mask.py" line="720"/>
        <source>Update the current mask</source>
        <translation>Mettre à jour le masque existant</translation>
    </message>
    <message>
        <location filename="../aeag_mask.py" line="259"/>
        <source>Documentation</source>
        <translation>Documentation</translation>
    </message>
    <message>
        <location filename="../aeag_mask.py" line="844"/>
        <source>Invalid dataProvider. The mask remains in memory. Check file name, format and extension.</source>
        <translation>dataProvider invalide, la couche reste en mémoire. Vérifier l&apos;adéquation nom de fichier/format/extension</translation>
    </message>
    <message>
        <location filename="../aeag_mask.py" line="847"/>
        <source>No GeometryType. The mask remains in memory. Check file name, format and extension.</source>
        <translation>Geométrie invalide, la couche reste en mémoire. Vérifier l&apos;adéquation nom de fichier/format/extension</translation>
    </message>
    <message>
        <location filename="../aeag_mask.py" line="858"/>
        <source>The mask remains in memory. Check file name, format and extension.</source>
        <translation>La couche reste en mémoire. Vérifier l&apos;adéquation nom de fichier/format/extension</translation>
    </message>
    <message>
        <location filename="../aeag_mask.py"/>
        <source>Cannot create layer</source>
        <translation>Impossible de créer la couche</translation>
    </message>
    <message>
        <location filename="../aeag_mask.py" />
        <source>Attribute type unsupported</source>
        <translation>Type d&apos;attribut non supporté</translation>
    </message>
    <message>
        <location filename="../aeag_mask.py" />
        <source>Attribute creation failed</source>
        <translation>Echec de création d&apos;attribut</translation>
    </message>
    <message>
        <location filename="../aeag_mask.py" />
        <source>Projection error</source>
        <translation>Erreur de projection</translation>
    </message>
    <message>
        <location filename="../aeag_mask.py" />
        <source>Feature write failed</source>
        <translation>Echec d&apos;écriture</translation>
    </message>
    <message>
        <location filename="../aeag_mask.py" />
        <source>Invalid layer</source>
        <translation>Couche invalide</translation>
    </message>
    <message>
        <location filename="../aeag_mask.py" />
        <source>Invalid layer</source>
        <translation>Couche invalide</translation>
    </message>
    <message>
        <location filename="../aeag_mask.py" />
        <source>Metadata saving error</source>
        <translation>Sauvegarde des métadonnées impossible</translation>
    </message>
    <message>
        <location filename="../aeag_mask.py" line="244"/>
        <source>Documentation</source>
        <translation>Documentation</translation>
    </message>

</context>
</TS>
