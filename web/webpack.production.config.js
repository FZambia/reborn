var path = require('path');
var webpack = require('webpack');
var HtmlWebpackPlugin = require('html-webpack-plugin');
var CopyWebpackPlugin = require('copy-webpack-plugin');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var CleanWebpackPlugin = require('clean-webpack-plugin');

module.exports = {
    entry: [
        './src/js/app.jsx',
        './src/less/style.less'
    ],
    output: {
        path: path.resolve(__dirname, 'dist'),
        publicPath: '/',
        filename: '[name].[hash].js'
    },
    resolve: {
        extensions: ['.js', '.jsx']
    },
    plugins: [
        new webpack.DefinePlugin({
            'process.env': {
              'NODE_ENV': JSON.stringify('production')
            }
        }),
        new webpack.optimize.UglifyJsPlugin(),
        new CleanWebpackPlugin([
            path.resolve(__dirname, 'dist')
        ]),
        new ExtractTextPlugin({
            filename: 'main.[hash].css',
            disable: false,
            allChunks: true
        }),
        new webpack.optimize.CommonsChunkPlugin({
            name: 'vendor',
            filename: 'vendor.bundle.[hash].js'
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
