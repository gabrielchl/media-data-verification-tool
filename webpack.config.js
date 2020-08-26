var path = require('path');

module.exports = {
    entry: {
        'home': './src/home.js',
        'contribute': './src/contribute.js',
        'my-contributions': './src/my-contributions.js',
    },
    output: {
        path: path.resolve(__dirname, 'mdvt/static/js'),
        filename: '[name].js',
    },
    plugins: []
}