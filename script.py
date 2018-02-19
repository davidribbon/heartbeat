from PyQt4.QtCore import *
import urllib2, json
appcode = "place your code here"
appID = "place your code here"
coordinates = "52.471868,-1.897253"#place your coordinates here
#create the containing layer:
vl = QgsVectorLayer("Polygon?crs=EPSG:102013", "temporary_polygons", "memory")
pr = vl.dataProvider()
# add fields
pr.addAttributes([QgsField("time", QVariant.Int),
                    QgsField("departure", QVariant.String),
                    QgsField("area", QVariant.Double)])
vl.updateFields()
#let's define some projection magic to get equal area:

src_crs = QgsCoordinateReferenceSystem(4326)
dest_crs = QgsCoordinateReferenceSystem(102013)
xform = QgsCoordinateTransform(src_crs, dest_crs)

#iterate through the times:
for hour in range(0,24):
    if hour<10:
        timestamp='2017-12-01T0' + str(hour) + ':00:00Z02'
    else:
        timestamp='2017-12-01T' + str(hour) + ':00:00Z02'
    
    url = "https://isoline.route.cit.api.here.com/routing/7.2/calculateisoline.json?app_id=" + appID + "&app_code=" + appcode + "&mode=shortest;car;traffic:enabled&start=geo!" + coordinates + "&maxpoints=500&departure=" + timestamp + "&range=600,1200,1800&rangetype=time&jsonAttributes=41"
    response = urllib2.urlopen(url)
    data = json.load(response)
    #parse the polys:
    for polygon in reversed(data['response']['isoline']):
        pointArray = []
        for ind in range(0,len(polygon['component'][0]['shape'])):
            if ind%2 == 1:
                pointArray.append(xform.transform(QgsPoint(polygon['component'][0]['shape'][ind], polygon['component'][0]['shape'][ind-1])))
        #combine to polygon:
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPolygon([pointArray]))
        feature.setAttributes([polygon['range'], timestamp[0:16], feature.geometry().area()/1000000])
        pr.addFeatures([feature])

QgsMapLayerRegistry.instance().addMapLayer(vl)

