var $ = require("jquery");
var React = require("react");
var classNames = require('classnames');


function htmlDecode(input) {
    var e = document.createElement('div');
    e.innerHTML = input;
    return e.childNodes.length === 0 ? "" : e.childNodes[0].nodeValue;
}

class Entry extends React.Component {
    handleFavoriteClick(e) {
        this.props.handleFavoriteClick(this.props.entryId, !this.props.isFavorite);
        e.preventDefault();
    }

    render() {
        var favoriteClasses = classNames({
            'glyphicon': true,
            'glyphicon-star-empty': !this.props.isFavorite,
            'glyphicon-star': this.props.isFavorite,
            'entry-favorite': true
        });

        var content = "";
        if (this.props.content) {
            content = this.props.content;
        } else if (["gif", "jpg", "jpeg", "png"].indexOf(this.props.url.slice(-3).toLowerCase()) > -1) {
            content = '<img src="'+ this.props.url +'" />';
        } else if (this.props.url.endsWith("gifv") || this.props.url.endsWith("webm")) {
            var contentURL = this.props.url.replace("gifv", "mp4");
            contentURL = contentURL.replace("http://", "//");
            content = '<video preload="auto" autoplay="autoplay" loop="loop" style="width: 100%;"> <source src="'+contentURL+'" type="video/mp4"></source> </video>';
        }

        var contentClasses = classNames({
            'entry-content': true,
            'hidden': !Boolean(content)
        });

        return (
            <div ref="entry" className="entry">
                <div className="entry-head">
                    <span className={favoriteClasses} onClick={this.handleFavoriteClick.bind(this)}></span>
                    &nbsp;
                    <a className="entry-title" href={this.props.url} target="_blank">
                        {this.props.title}
                    </a>
                    &nbsp;
                    <a className="entry-source" target="_blank" href={this.props.permalink}>
                        {this.props.providerName}:{this.props.source}
                    </a>
                </div>
                <div className={contentClasses} dangerouslySetInnerHTML={{__html: content}}></div>
            </div>
        )
    }
}

module.exports = Entry;