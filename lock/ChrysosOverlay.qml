// Chrysos Heirs lock-screen overlay.
//
// Draws only when the current theme ships chrysos-lock.json (every
// chrysos-heirs* theme does). For any other theme the file is missing,
// `active` stays false and the lock looks exactly like Omarchy's stock one.
//
// Layout, inspired by the Honkai: Star Rail title screen:
//   - the wallpaper, sharp, under a scrim in the theme's background colour
//   - the HSR logo, glowing in the heir's accent
//   - a serif clock + date above the (stock, untouched) password field
//   - the heir's name, epithet and bond, over a gradient "thread" in the
//     same colours as the active window border.
import QtQuick
import QtQuick.Effects
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Commons as Commons

Item {
  id: overlay

  property string backgroundPath: ""
  property bool loadBackground: true

  readonly property string themeDir: Quickshell.env("HOME") + "/.local/state/omarchy/current/theme"
  property var heir: null
  readonly property bool active: heir !== null
  readonly property bool light: active && heir.mode === "light"
  readonly property string serif: "C059"
  readonly property color bgColor: active ? heir.background : "#000000"
  function veil(a) { return Qt.rgba(bgColor.r, bgColor.g, bgColor.b, a) }

  visible: active

  function reload() {
    try {
      const raw = spec.text()
      overlay.heir = raw && raw.length > 0 ? JSON.parse(raw) : null
    } catch (e) {
      console.warn("chrysos-lock: cannot read " + spec.path + ": " + e)
      overlay.heir = null
    }
  }

  FileView {
    id: spec
    path: overlay.themeDir + "/chrysos-lock.json"
    watchChanges: true
    printErrors: false
    blockLoading: true
    onLoaded: overlay.reload()
    onLoadFailed: overlay.heir = null
    onFileChanged: reload()
  }

  // A theme switch swaps the whole theme directory, which a file watch can miss.
  // The palette always changes with it, so re-read on that too, and on lock.
  Connections {
    target: Commons.Color
    function onBackgroundChanged() { spec.reload() }
  }
  Component.onCompleted: reload()
  onLoadBackgroundChanged: if (loadBackground) spec.reload()

  // ---- wallpaper, sharp, with a scrim -------------------------------------
  Image {
    id: art
    anchors.fill: parent
    visible: overlay.active && overlay.loadBackground
    source: visible && overlay.backgroundPath ? "file://" + overlay.backgroundPath : ""
    fillMode: Image.PreserveAspectCrop
    asynchronous: true
    cache: true
    sourceSize: Qt.size(width, height)
  }

  Rectangle {
    anchors.fill: parent
    visible: art.visible
    gradient: Gradient {
      GradientStop { position: 0.0; color: overlay.veil(0.55) }
      GradientStop { position: 0.38; color: overlay.veil(0.30) }
      GradientStop { position: 0.62; color: overlay.veil(0.45) }
      GradientStop { position: 1.0; color: overlay.veil(0.92) }
    }
  }

  // Soft pool of shadow behind the field and clock so they read on any art.
  Rectangle {
    width: Math.min(parent.width * 0.6, 980)
    height: width * 0.62
    anchors.centerIn: parent
    anchors.verticalCenterOffset: -parent.height * 0.06
    radius: width / 2
    color: overlay.active ? overlay.heir.background : "black"
    opacity: overlay.light ? 0.35 : 0.5
    layer.enabled: true
    layer.effect: MultiEffect { blurEnabled: true; blur: 1.0; blurMax: 64 }
  }

  // ---- logo ----------------------------------------------------------------
  Image {
    id: logo
    source: overlay.active ? "file://" + overlay.themeDir + "/chrysos-lock-logo.png" : ""
    width: Math.min(parent.width * 0.21, 560)
    fillMode: Image.PreserveAspectFit
    smooth: true
    mipmap: true
    anchors.horizontalCenter: parent.horizontalCenter
    anchors.top: parent.top
    anchors.topMargin: parent.height * 0.05
    layer.enabled: true
    layer.effect: MultiEffect {
      shadowEnabled: true
      shadowColor: overlay.active ? (overlay.light ? overlay.heir.foreground : overlay.heir.accent) : "white"
      shadowBlur: 1.0
      shadowOpacity: overlay.light ? 0.9 : 0.85
      shadowHorizontalOffset: 0
      shadowVerticalOffset: 0
    }
  }

  // ---- clock ---------------------------------------------------------------
  property date now: new Date()
  Timer {
    interval: 1000
    running: overlay.active && overlay.visible
    repeat: true
    triggeredOnStart: true
    onTriggered: overlay.now = new Date()
  }

  Column {
    anchors.horizontalCenter: parent.horizontalCenter
    anchors.bottom: parent.verticalCenter
    anchors.bottomMargin: Math.round(overlay.height * 0.06)
    spacing: 4

    Text {
      textFormat: Text.PlainText
      anchors.horizontalCenter: parent.horizontalCenter
      text: overlay.now.toLocaleTimeString(Qt.locale(Commons.I18n.formatLocale), Locale.ShortFormat)
      color: overlay.active ? overlay.heir.foreground : "white"
      font.family: overlay.serif
      font.pixelSize: Math.round(Math.min(overlay.height * 0.095, 140))
      style: overlay.light ? Text.Normal : Text.Raised
      styleColor: overlay.veil(0.6)
    }
    Text {
      textFormat: Text.PlainText
      anchors.horizontalCenter: parent.horizontalCenter
      text: overlay.now.toLocaleDateString(Qt.locale(Commons.I18n.formatLocale), "dddd, d MMMM")
      color: overlay.active ? overlay.heir.subtle : "white"
      font.family: overlay.serif
      font.italic: true
      font.pixelSize: Math.round(Math.min(overlay.height * 0.024, 30))
    }
  }

  // ---- heir, epithet, bond -------------------------------------------------
  Column {
    id: heirBlock
    anchors.horizontalCenter: parent.horizontalCenter
    anchors.bottom: parent.bottom
    anchors.bottomMargin: parent.height * 0.07
    spacing: 10
    width: Math.min(parent.width * 0.5, 900)

    Text {
      textFormat: Text.PlainText
      anchors.horizontalCenter: parent.horizontalCenter
      text: overlay.active ? overlay.heir.name.toUpperCase() : ""
      color: overlay.active ? overlay.heir.foreground : "white"
      font.family: overlay.serif
      font.pixelSize: Math.round(Math.min(overlay.height * 0.034, 42))
      font.letterSpacing: Math.round(Math.min(overlay.height * 0.034, 42)) * 0.35
    }

    // The bond thread: the same colours as the focused window's border.
    Rectangle {
      width: parent.width
      height: 2
      radius: 1
      gradient: Gradient {
        orientation: Gradient.Horizontal
        GradientStop { position: 0.0; color: "transparent" }
        GradientStop { position: 0.15; color: overlay.active ? overlay.heir.thread[0] : "white" }
        GradientStop { position: 0.5; color: overlay.active ? overlay.heir.thread[1] : "white" }
        GradientStop { position: 0.85; color: overlay.active ? overlay.heir.thread[overlay.heir.thread.length - 1] : "white" }
        GradientStop { position: 1.0; color: "transparent" }
      }
    }

    Text {
      textFormat: Text.PlainText
      anchors.horizontalCenter: parent.horizontalCenter
      text: overlay.active ? overlay.heir.epithet + "  ·  " + overlay.heir.bond : ""
      color: overlay.active ? overlay.heir.accent : "white"
      font.family: overlay.serif
      font.italic: true
      font.pixelSize: Math.round(Math.min(overlay.height * 0.022, 26))
    }

    Text {
      textFormat: Text.PlainText
      anchors.horizontalCenter: parent.horizontalCenter
      text: overlay.active ? overlay.heir.flame.toUpperCase() : ""
      color: overlay.active ? overlay.heir.subtle : "white"
      opacity: 0.8
      font.family: overlay.serif
      font.pixelSize: Math.round(Math.min(overlay.height * 0.014, 16))
      font.letterSpacing: Math.round(Math.min(overlay.height * 0.014, 16)) * 0.3
    }
  }
}
