var React = require("react");
var classNames = require('classnames');


class Overlay extends React.Component {
    render () {
        var names = {
            'md-overlay': true,
            'md-overlay-show': this.props.show,
        };
        var extraClass = this.props.extraClass;
        names[extraClass] = true;
        var classes = classNames(names);
        return (
            <div className={classes} onClick={this.props.handleClick}>
                {this.props.loading ? <img src={this.props.loaderUrl} />: ""}
            </div>
        );
    }
}

Overlay.defaultProps = {
    handleClick: function(){},
    loading: false,
    extraClass: "",
    loaderUrl: "/img/loading-bars.svg"
};

module.exports = Overlay;