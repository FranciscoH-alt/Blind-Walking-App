import QtQuick 2.12
import QtQuick.Window 2.12
import QtLocation 5.12
import QtPositioning 5.12
import QtQuick.Controls 2.12

Window {
    visible: true
    width: 640
    height: 480
    title: qsTr("GPS Navigation Map")

    Plugin {
        id: mapPlugin
        name: "osm" // OpenStreetMap
    }

    Map {
        id: mapObj
        objectName: "mapObj"
        anchors.fill: parent
        plugin: mapPlugin
        center: QtPositioning.coordinate(42.672, -83.215)
        zoomLevel: 16

        MapQuickItem {
            id: myMarker
            anchorPoint.x: 12
            anchorPoint.y: 12
            coordinate: QtPositioning.coordinate(mapObj.latitude, mapObj.longitude)
            sourceItem: Rectangle {
                width: 24; height: 24
                color: "red"
                radius: 12
            }
        }

        property real latitude: 42.672
        property real longitude: -83.215
    }

    Button {
        text: "Retrace Steps"
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        onClicked: gpsNav.retrace_steps()
    }
}
