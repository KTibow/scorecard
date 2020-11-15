if (typeof document.createStyleSheet === "undefined") {
    document.createStyleSheet = (function () {
        function createStyleSheet(href) {
            if (typeof href !== "undefined") {
                var element = document.createElement("link");
                element.type = "text/css";
                element.rel = "stylesheet";
                element.href = href;
            } else {
                var element = document.createElement("style");
                element.type = "text/css";
            }

            document.getElementsByTagName("head")[0].appendChild(element);
            var sheet = document.styleSheets[document.styleSheets.length - 1];

            if (typeof sheet.addRule === "undefined") sheet.addRule = addRule;

            if (typeof sheet.removeRule === "undefined")
                sheet.removeRule = sheet.deleteRule;

            return sheet;
        }

        function addRule(selectorText, cssText, index) {
            if (typeof index === "undefined") index = this.cssRules.length;

            this.insertRule(selectorText + " {" + cssText + "}", index);
        }

        return createStyleSheet;
    })();
}
