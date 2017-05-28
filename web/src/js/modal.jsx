var $ = require("jquery");
var React = require("react");
var Overlay = require("./overlay.jsx");
var classNames = require('classnames');

class Modal extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            show: this.props.show
        }
    }

    render() {
        var classes = classNames({
            "md-modal": true,
            "md-effect-1": true,
            "md-show": this.state.show
        });
        return (
            <div>
                <div ref="modal" className={classes}>
                    <div className="md-content">
                        <h3>{this.props.header}</h3>
                        <div className="md-body">
                            {this.props.content}
                        </div>
                    </div>
                </div>
                <Overlay show={this.state.show} ref="overlay" />
            </div>
        );
    }
}

module.exports = Modal;
