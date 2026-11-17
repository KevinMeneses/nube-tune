// Imprime el id de la primera ventana cuyo título contiene el argumento (para screencapture -l, sin traer la ventana al frente).
import CoreGraphics
let l = CGWindowListCopyWindowInfo([.optionAll], kCGNullWindowID) as! [[String: Any]]
for w in l { if let n = w["kCGWindowName"] as? String, n.contains(CommandLine.arguments[1]) { print(w["kCGWindowNumber"]!); break } }
