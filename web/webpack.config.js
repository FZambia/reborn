var path = require('path');
var webpack = require('webpack');
var BrowserSyncPlugin = require('browser-sync-webpack-plugin');
var HtmlWebpackPlugin = require('html-webpack-plugin');
var CopyWebpackPlugin = require('copy-webpack-plugin');
var HistoryApiFallback = require('connect-history-api-fallback');
var ExtractTextPlugin = require('extract-text-webpack-plugin');

var definePlugin = new webpack.DefinePlugin({
    __DEV__: JSON.stringify(JSON.parse(process.env.BUILD_DEV || 'true'))
});

module.exports = {
    entry: [
        './src/js/app.jsx',
        './src/less/style.less'
    ],
    devtool: 'cheap-source-map',
    devServer: {
        port: 5000,
        historyApiFallback: {
            index: 'index.html'
        }
    },
    output: {
        path: path.resolve(__dirname, 'build'),
        publicPath: '/',
        filename: 'bundle.js'
    },
    resolve: {
        extensions: ['.js', '.jsx']
    },
    watch: true,
    plugins: [
        definePlugin,
        new ExtractTextPlugin({
            filename: 'main.css',
            disable: false,
            allChunks: true
        }),
        new webpack.optimize.CommonsChunkPlugin({
            name: 'vendor',
            filename: 'vendor.bundle.js'
        }),
        new BrowserSyncPlugin({
            host: process.env.IP || 'localhost',
            port: process.env.PORT || 3000,
            server: {
                baseDir: ['./build/'],
                middleware: [HistoryApiFallback()]
            }
        }),
        new CopyWebpackPlugin([
            {
                from: 'src/vendor'
            },
            {
                from: 'src/img',
                to: 'img'
            },
            {
                from: 'src/misc',
                to: ''
            }
        ]),
        new HtmlWebpackPlugin({
            template: 'src/index.html'
        })
    ],
    module: {
        loaders: [
            {
                test: /\.jsx?$/,
                loader: 'babel-loader',
                query: {
                    presets: ['es2015', 'react']
                }
            },
            {
                test: /\.less$/,
                loader: ExtractTextPlugin.extract({
                    fallback: 'style-loader',
                    use: "css-loader!less-loader"
                })
            }
        ]
    }
};
