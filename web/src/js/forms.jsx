var $ = require("jquery");
var React = require("react");
var ReactDOM = require("react-dom");
var Router = require('react-router');
var Link = Router.Link;
var Hello = require("hellojs");
var classNames = require('classnames');


class CategoryForm extends React.Component {

    constructor(props) {
        super(props);
        this.state = this.getInitialState();
    }

    getInitialState() {
        return {
            category: {
                "name": ""
            },
            submitClass: "glyphicon-floppy-save"
        }
    }

    componentWillMount() {
        if (this.props.category) {
            this.setState({category: this.props.category});
        } else {
            this.setState(this.getInitialState());
        }
    }

    componentWillReceiveProps(nextProps) {
        if (nextProps.category) {
            if (this.props.category && this.props.category.id == nextProps.category.id) {
                return
            }
            this.setState({category: nextProps.category});
        } else {
            this.setState(this.getInitialState());
        }
    }

    submitSucceded() {
        this.setState({
            "submitClass": "glyphicon-floppy-saved"
        })
        setTimeout(function(){
            this.setState({
                "submitClass": "glyphicon-floppy-save"
            }) 
        }.bind(this), 1000);
    }

    submitFailed() {
        this.setState({
            "submitClass": "glyphicon-floppy-remove"
        })
        setTimeout(function(){
            this.setState({
                "submitClass": "glyphicon-floppy-save"
            }) 
        }.bind(this), 1000);
    }

    handleSubmit(e) {
        var id = this.props.category?this.props.category.id:null;
        var name = ReactDOM.findDOMNode(this.refs.name).value;
        if (!id) {
            this.props.createCategory(name, this.submitSucceded.bind(this), this.submitFailed.bind(this));
        } else {
            this.props.updateCategory(id, name, this.submitSucceded.bind(this), this.submitFailed.bind(this));
        }
        e.preventDefault();
    }

    handleDelete(e) {
        var id = this.props.category.id;
        this.props.deleteCategory(id);
        return false;
    }

    handleChange(e) {
        this.setState({category: {"name": e.target.value}});
    }

    render() {
        var header = this.props.category?"Edit category": "New category";
        var name = this.state.category.name;
        var submitClassNames = {
            "glyphicon": true,
            "button-submit": true
        };
        submitClassNames[this.state.submitClass] = true;
        var submitClasses = classNames(submitClassNames);
        return (
            <div className="form-container">
                <div className="form-header">{header}</div>
                <form className="form-horizontal" ref="form" role="form" onSubmit={this.handleSubmit.bind(this)}>
                    <div className="form-group">
                        <div className="col-sm-12">
                            <input type="text" autoComplete="off" ref="name" name="name" className="form-control" placeholder="category name, unique and meaningful for you" onChange={this.handleChange.bind(this)} value={name} />
                        </div>
                    </div>
                    <div className="form-group">
                        <div className="col-sm-12 button-container">
                            <span className={submitClasses} title="Save" onClick={this.handleSubmit.bind(this)}></span>
                            {this.props.category?<span className="glyphicon glyphicon-remove button-remove" title="Remove" onClick={this.handleDelete.bind(this)}></span>:""}
                        </div>
                    </div>
                </form>
            </div>
        );
    }
}

class CategoryFormRow extends React.Component {
    onChange(e) {
        this.props.onChange(parseInt(e.target.value), !this.props.selected);
    }
    render() {
        var svgStyle = {
            strokeDasharray: '126.369537353516px, 126.369537353516px',
            strokeDashoffset: '0px',
            WebkitTransition: 'stroke-dashoffset 0.2s ease-in-out 0s',
            transition: 'stroke-dashoffset 0.2s ease-in-out 0s'
        };
        var classes = classNames({
            'hidden': !this.props.selected
        });
        return (
            <li>
                <input id={"cb" + this.props.value} name="category" type="checkbox" value={this.props.value} checked={this.props.selected} onChange={this.onChange.bind(this)} />
                <label htmlFor={"cb" + this.props.value}>{this.props.name}</label>
                <svg className={classes} viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                    <path d="M16.667,62.167c3.109,5.55,7.217,10.591,10.926,15.75 c2.614,3.636,5.149,7.519,8.161,10.853c-0.046-0.051,1.959,2.414,2.692,2.343c0.895-0.088,6.958-8.511,6.014-7.3 c5.997-7.695,11.68-15.463,16.931-23.696c6.393-10.025,12.235-20.373,18.104-30.707C82.004,24.988,84.802,20.601,87,16" style={svgStyle}></path>
                </svg>
            </li>
        );
    }
}

function clone(obj) {
    if (null == obj || "object" != typeof obj) return obj;
    var copy = obj.constructor();
    for (var attr in obj) {
        if (obj.hasOwnProperty(attr)) copy[attr] = obj[attr];
    }
    return copy;
}

class SubscriptionForm extends React.Component {

    constructor(props) {
        super(props);
        this.state = this.getInitialState();
    }

    getInitialState() {
        return {
            subscription: {
                "score": "",
                "categories": [],
                "source": ""
            },
            submitClass: "glyphicon-floppy-save"
        }
    }

    componentWillMount() {
        if (this.props.subscription) {
            this.setState({subscription: this.props.subscription});
        } else {
            this.setState(this.getInitialState());
        }
    }

    componentWillReceiveProps(nextProps) {
        if (nextProps.subscription) {
            if (this.props.subscription && this.props.subscription.id == nextProps.subscription.id) {
                return
            }
            this.setState({subscription: nextProps.subscription});
        } else {
            this.setState(this.getInitialState());
        }
    }

    submitSucceded() {
        this.setState({
            "submitClass": "glyphicon-floppy-saved"
        })
        setTimeout(function(){
            this.setState({
                "submitClass": "glyphicon-floppy-save"
            }) 
        }.bind(this), 1000);
    }

    submitFailed() {
        this.setState({
            "submitClass": "glyphicon-floppy-remove"
        })
        setTimeout(function(){
            this.setState({
                "submitClass": "glyphicon-floppy-save"
            }) 
        }.bind(this), 1000);
    }

    handleSubmit(e) {
        var id = this.props.subscription?this.props.subscription.id:null;
        var data = $(ReactDOM.findDOMNode(this.refs.form)).serializeArray();
        var provider = "";
        var name = "";
        var score = "";
        var categories = [];
        for (var i in data) {
            var item = data[i];
            var value = item["value"];
            switch (item["name"]) {
                case "provider":
                    provider = value;
                    break;
                case "name":
                    name = value;
                    break;
                case "score":
                    score = value;
                    break;
                case "category":
                    categories.push(value);
            }
        }
        if (!id) {
            this.props.createSubscription(provider, name, score, categories, this.submitSucceded.bind(this), this.submitFailed.bind(this));
        } else {
            this.props.updateSubscription(id, provider, name, score, categories, this.submitSucceded.bind(this), this.submitFailed.bind(this));
        }
        e.preventDefault();
    }

    handleDelete(e) {
        var id = this.props.subscription.id;
        this.props.deleteSubscription(id);
        return false;
    }

    handleNameChange(e) {
        var subscription = clone(this.state.subscription);
        subscription["source"] = e.target.value;
        this.setState({subscription: subscription});
    }

    handleScoreChange(e) {
        var subscription = clone(this.state.subscription);
        subscription["score"] = e.target.value;
        this.setState({subscription: subscription});
    }

    handleCategoryChange(categoryId, selected) {
        var subscription = clone(this.state.subscription);
        var current_categories = subscription["categories"].slice(0);
        if (selected) {
            if (current_categories.indexOf(categoryId) === -1) {
                current_categories.push(categoryId);
            }
        } else {
            var index = current_categories.indexOf(categoryId);
            if (index > -1) {
                current_categories.splice(index, 1);
            }
        }
        subscription["categories"] = current_categories;
        this.setState({subscription: subscription});
    }

    render() {
        var rows = [];
        this.props.categories.forEach(function (item) {
            var selected = this.state.subscription.categories.indexOf(item.id) > -1;
            rows.push(<CategoryFormRow name={item.name} value={item.id} selected={selected} key={item.id} onChange={this.handleCategoryChange.bind(this)} />)
        }.bind(this));

        var submitClassNames = {
            "glyphicon": true,
            "button-submit": true
        };
        submitClassNames[this.state.submitClass] = true;
        var submitClasses = classNames(submitClassNames);

        return (
            <div className="form-container">
                <div className="form-header">
                    {this.props.subscription?<span>Edit {this.props.provider.name} subscription</span>:<span>New {this.props.provider.name} subscription</span>}
                </div>
                <form className="form-horizontal ac-custom" ref="form" role="form" onSubmit={this.handleSubmit.bind(this)}>
                    <input type="hidden" name="provider" value={this.props.provider.id} />
                    <div className="form-group">
                        <div className="col-sm-12">
                            <input type="text" name="name" autoComplete="off" className="form-control" placeholder={this.props.provider.name + " source"} onChange={this.handleNameChange.bind(this)} value={this.state.subscription.source} />
                        </div>
                    </div>
                    <div className="form-group">
                        <div className="col-sm-12">
                            <input type="text" name="score" autoComplete="off" className="form-control" placeholder="minimal score, depends on provider, source and your taste" onChange={this.handleScoreChange.bind(this)} value={this.state.subscription.score} />
                        </div>
                    </div>
                    <div className="form-group">
                        <div className="col-sm-12">
                            <h5>Categories:</h5>
                        </div>
                        <div className="col-sm-12">
                            <ul>
                            {rows}
                            </ul>
                        </div>
                    </div>
                    <div className="form-group">
                        <div className="col-sm-12 button-container">
                            <span className={submitClasses} title="Save" onClick={this.handleSubmit.bind(this)}></span>
                            {this.props.subscription?<span className="glyphicon glyphicon-remove button-remove" onClick={this.handleDelete.bind(this)}></span>:""}
                        </div>
                    </div>
                </form>
            </div>
        );
    }
}

class LoginForm extends React.Component {

    handleFacebookLogin(e) {
        var self = this;
        Hello.init({
            facebook: this.props.fbAppId
        }, {redirect_uri: this.props.redirectURI});
        Hello.login('facebook', {}, function(data) {
            var accessToken = data.authResponse.access_token;
            self.props.handleAccessToken(data.network, accessToken);
        });
        e.preventDefault();
    }

    handleSubmit(e) {
        this.props.handleAuth(ReactDOM.findDOMNode(this.refs.login).value, ReactDOM.findDOMNode(this.refs.password).value);
        e.preventDefault();
    }

    render() {
        return (
            <div className="form-container">
                <form className="form-horizontal" ref="form" role="form" onSubmit={this.handleSubmit.bind(this)}>
                    <div className="form-group">
                        <div className="col-sm-12">
                            <input type="text" ref="login" autoComplete="off" name="login" className="form-control" placeholder="login" />
                        </div>
                    </div>
                    <div className="form-group">
                        <div className="col-sm-12">
                            <input type="password" ref="password" autoComplete="off" name="password" className="form-control" placeholder="password" />
                        </div>
                    </div>
                    <div className="form-group">
                        <div className="col-sm-12 button-container">
                            <input type="submit" style={{"visibility": "hidden"}} />
                            <span className="glyphicon glyphicon-log-in button-submit" title="Save" onClick={this.handleSubmit.bind(this)}></span>
                        </div>
                    </div>
                </form>
                {/*<a href="#" className="login fb-login" onClick={this.handleFacebookLogin.bind(this)}>log in with Facebook</a>*/}
            </div>
        );
    }
}

module.exports.CategoryForm = CategoryForm;
module.exports.SubscriptionForm = SubscriptionForm;
module.exports.LoginForm = LoginForm;
