export function getUrlParam(key, default_value=null) {
    var match = decodeURIComponent(window.location.href).match(key + '=([^&]*)');
    if (match == null) {
        return default_value;
    } else {
        return match[1];
    }
}
