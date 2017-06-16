var $ = require("jquery");
var Sidebar = require("./sidebar.jsx");
var Overlay = require("./overlay.jsx");
var Modal = require("./modal.jsx");
var forms = require("./forms.jsx");
var CategoryForm = forms.CategoryForm;
var SubscriptionForm = forms.SubscriptionForm;
var LoginForm = forms.LoginForm;
var Filter = require("./filter.jsx");
var Entry = require("./entry.jsx");
var Paginator = require("./paginator.jsx");

var React = require('react');
var ReactDOM = require('react-dom');

var reactRouter = require('react-router');
var Router = reactRouter.Router;
var Route = reactRouter.Route;
var Link = reactRouter.Link;
var IndexRoute = reactRouter.IndexRoute;
import { browserHistory } from 'react-router';
const queryString = require('query-string');

$.ajaxSettings.traditional = true;

var Auth = {
    setToken: function(token) {
        localStorage.token = token;
    },
    getToken: function() {
        return localStorage.token;
    },
    deleteToken: function() {
        delete localStorage.token;
    }
};

class App extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            title: "",
            telegram_bot_name: "",
            dashboard: {},
            categories: [],
            providers: [],
            providersByID: {},
            entries:[],
            totalCount: 0,
            currentPage: parseInt(this.props.location.query["p"]) || 1,
            hasNextPage: false,
            hasPreviousPage: false,
            initialized: false,
            loggedIn: false,
            loading: false,
            showLoginForm: false
        };
    }

    ajax_get(url, data, callback, errback) {
        data["paginate_by"] = 100;
        $.ajax({
            url: url,
            data: data,
            dataType: 'json',
            headers: {
                "Authorization": "Token " + (Auth.getToken()?Auth.getToken():"")
            },
            success: function (data) {
                callback(data);
            }.bind(this),
            error: function (xhr) {
                if (xhr.status == 401) {
                    this.setState({loggedIn: false});
                    console.log(this.state);
                }
                if (errback) {
                    errback(xhr.status, xhr.responseJSON);
                }
            }.bind(this)
        });
    }

    ajax_action(url, method, data, loading, callback, errback) {
        if (loading) {
            this.show_loading_overlay();
        }

        var options = {
            url: url,
            method: method,
            dataType: 'json',
            headers: {
                "Authorization": "Token " + (localStorage.token?localStorage.token:"")
            },
            success: function (data) {
                if (loading) {
                    this.hide_loading_overlay();
                }
                callback(data);
            }.bind(this),
            error: function (xhr) {
                if (xhr.status === 401) {
                    this.setState({loggedIn: false});
                }
                if (loading) {
                    this.hide_loading_overlay();
                }
                if (errback) {
                    errback(xhr.status, xhr.responseJSON);
                }
            }.bind(this)
        };

        if (method === "GET") {
            options.data = data;
        } else {
            options.data = JSON.stringify(data);
            options.contentType = 'application/json; charset=utf-8';
        }

        $.ajax(options);
    }

    componentWillMount () {
        this.initialize();
    }

    initialize() {
        this.ajax_action(this.props.initEndpoint, "GET", {}, false, function(data){
            this.setState({title: data.title});
            if (data.is_authenticated) {
                var providers = data.providers;
                var positions = {};
                var providersByID = {};
                for (var i in providers) {
                    providers[i]["subscriptions"] = [];
                    positions[providers[i]["id"]] = i;
                    providersByID[providers[i]["id"]] = providers[i];
                }
                var subscriptions = data.subscriptions;
                for (var i in subscriptions) {
                    var providerID = subscriptions[i]["source"]["provider"];
                    providers[positions[providerID]]["subscriptions"].push(subscriptions[i]);
                }

                this.setState({
                    loggedIn: true,
                    providers: providers,
                    providersByID: providersByID,
                    categories: data.categories,
                    subscriptions: subscriptions,
                    initialized: true,
                    dashboard: data.dashboard,
                    telegramBotName: data.telegram_bot_name
                });
            } else {
                this.setState({
                    initialized: false,
                    showLoginForm: true
                });
            }
        }.bind(this));
    }

    show_loading_overlay() {
        this.setState({loading: true});
    }

    hide_loading_overlay() {
        this.setState({loading: false});
    }

    getPage() {
        return parseInt(this.props.location.query["p"] || 1);
    }

    loadEntries(loading, callback) {
        var page = this.getPage();

        var data = {
            paginate_by: this.props.paginateBy,
            page: page
        };

        var query = this.props.location.query;

        if ("category" in query) {
            data["category"] = parseInt(query["category"]);
        } else if ("subscription" in query) {
            var subscription_ids = [];
            subscription_ids.push(parseInt(query["subscription"]));
            data["subscription"] = subscription_ids;
        } else {
            // all entries
        }

        if ("search" in query) {
            data["search"] = query["search"];
        }

        if ("favorite" in query) {
            data["favorite"] = "on";
        }

        this.ajax_action(this.props.entryEndpoint, "GET", data, loading, function(data){
            this.setState({entries: data["results"]});
            this.setState({totalCount: data["count"]});
            this.setState({hasNextPage: data["next"] !== null});
            this.setState({hasPreviousPage: data["previous"] !== null});
            this.setState({currentPage: page});
            window.scrollTo(0, 0);
            if (callback) {
                callback();
            }
        }.bind(this), function() {
        }.bind(this));
    }

    createCategory(name, callback, errback) {
        this.ajax_action(this.props.categoryEndpoint, "POST", {"name": name}, true, function(data) {
            var categories = this.state.categories.slice(0);
            categories.push(data);
            this.setState({categories: categories});
            this.props.router.push("/dashboard/category/" + data.id + "/edit/");
            if (callback) {
                callback();
            }
        }.bind(this), function(data) {
            if (errback) {
                errback();
            }
        }.bind(this));
    }

    updateCategory(id, name, callback, errback) {
        this.ajax_action(this.props.categoryEndpoint + id + "/", "PATCH", {"name": name}, true, function(data) {
            var categories = this.state.categories.slice(0);
            for (var i in categories) {
                if (categories[i]["id"] == id) {
                    categories[i] = data;
                    break;
                }
            }
            this.setState({categories: categories});
            if (callback) {
                callback();
            }
        }.bind(this), function() {
            if (errback) {
                errback();
            }
        }.bind(this));
    }

    deleteCategory(id) {
        this.ajax_action(this.props.categoryEndpoint + id + "/", "DELETE", {}, true, function(data) {
            var categories = this.state.categories.slice(0);
            var index = -1;
            for (var i in categories) {
                if (categories[i]["id"] == id) {
                    index = i;
                    break;
                }
            }
            if (index > -1) {
                categories.splice(index, 1);
            }
            this.setState({categories: categories});
            this.props.router.push("/");
        }.bind(this));
    }

    createSubscription(providerId, source, score, categories, callback, errback) {
        var data = {
            provider: providerId,
            source: source,
            score: score,
            categories: categories
        };
        this.ajax_action(this.props.subscriptionEndpoint, "POST", data, true, function(data) {
            var provider;
            var providers = this.state.providers.slice(0);
            for (var i in providers) {
                provider = providers[i];
                if (provider.id == providerId) {
                    break;
                }
            }
            provider.subscriptions.push(data);
            this.setState({providers: providers});
            this.props.router.push("/dashboard/subscription/" + providerId + "/" + data.id + "/edit/");
            if (callback) {
                callback();
            }
        }.bind(this), function() {
            if (errback) {
                errback();
            }
        }.bind(this));
    }

    updateSubscription(subscriptionId, providerId, source, score, categories, callback, errback) {
        var data = {
            provider: providerId,
            source: source,
            score: score,
            categories: categories
        };
        this.ajax_action(this.props.subscriptionEndpoint + subscriptionId + "/", "PATCH", data, true, function(data) {
            var provider;
            var providers = this.state.providers.slice(0);
            for (var i in providers) {
                provider = providers[i];
                if (provider.id == providerId) {
                    break;
                }
            }
            for (var i in provider.subscriptions) {
                var subscription = provider.subscriptions[i];
                if (subscription.id == subscriptionId) {
                    provider.subscriptions[i] = data;
                    break;
                }
            }
            this.setState({providers: providers});
            if (callback) {
                callback();
            }
        }.bind(this), function(){
            if (errback) {
                errback();
            }
        }.bind(this));
    }

    deleteSubscription(subscriptionId) {
        this.ajax_action(this.props.subscriptionEndpoint + subscriptionId + "/", "DELETE", {}, true, function(data) {
            var provider;
            var providers = this.state.providers.slice(0);
            for (var i in providers) {
                provider = providers[i];
                var index = -1;
                for (var i in provider.subscriptions) {
                    var subscription = provider.subscriptions[i];
                    if (subscription.id == subscriptionId) {
                        index = i;
                        break;
                    }
                }
                if (index > -1) {
                    provider.subscriptions.splice(index, 1);
                    break;
                }
            }
            this.setState({providers: providers});
            this.props.router.push("/");
        }.bind(this));
    }

    handleLogin(login, password) {
        this.ajax_action(this.props.tokenEndpoint, "POST", {"username": login, "password": password}, true, function(data) {
            Auth.setToken(data.token);
            this.setState({loggedIn:true});
            this.initialize();
        }.bind(this), function(status, data) {
            console.log(status);
            console.log(data);
        }.bind(this));
    }

    handleAccessToken(network, accessToken) {
        this.ajax_action(this.props.tokenEndpoint + network + "/", "POST", {"access_token": accessToken}, true, function(data) {
            console.log(data);
            Auth.setToken(data.token);
            this.initialize();
            if (!this.state.loggedIn) {
                this.setState({loggedIn:true});
            }
        }.bind(this), function(status, data) {
            console.log(status);
            console.log(data);
        }.bind(this));
    }

    handleLogout() {
        this.ajax_action(this.props.logoutEndpoint, "POST", {}, true, function(data) {
            console.log(1);
            Auth.deleteToken();
            this.setState({loggedIn: false, showLoginForm: true});
        }.bind(this), function(status, data) {
            console.log(status);
            console.log(data);
        }.bind(this));
    }

    handleEntryFavoriteClick(entryId, isFavorite) {
        var data = {
            is_favorite: isFavorite
        };
        this.ajax_action(this.props.entryEndpoint + entryId + "/", "PATCH", data, true, function(data) {
            var entries = this.state.entries.slice(0);
            for (var i in entries) {
                if (entries[i]["id"] == entryId) {
                    entries[i] = data;
                    break;
                }
            }
            this.setState({entries: entries});
        }.bind(this));
    }

    render () {

        var childrenWithProps = React.Children.map(this.props.children, (Child, i) => {
            return React.cloneElement(Child, {
                app: this
            });
        });

        if (this.state.loggedIn) {
            return (
                <div className="app">
                    <div className="wrapper">
                        <div className="sidebar-wrapper">
                            <Sidebar ref="sidebar"
                                title={this.state.title}
                                categories={this.state.categories}
                                providers={this.state.providers}
                                handleLogout={this.handleLogout.bind(this)}
                                routes={this.props.routes}
                            />
                        </div>
                        <div className="content-wrapper">
                            {childrenWithProps}
                        </div>
                    </div>
                    <Overlay ref="loading_overlay" show={this.state.loading} loading={true} />
                </div>
            );
        } else {
            if (this.state.showLoginForm) {
                var loginForm = <LoginForm handleAuth={this.handleLogin.bind(this)}
                                           handleAccessToken={this.handleAccessToken.bind(this)}/>;
                return (
                    <Modal show={true} header="Please, log in" content={loginForm}/>
                );
            } else {
                return (
                    <Overlay ref="loading_overlay" show={this.state.loading} loading={true} />
                );
            }
        }
    }
}

App.defaultProps = {
    initEndpoint: "/api/v1/init/",
    categoryEndpoint: "/api/v1/category/",
    providerEndpoint: "/api/v1/provider/",
    subscriptionEndpoint: "/api/v1/subscription/",
    entryEndpoint: "/api/v1/entry/",
    tokenEndpoint: "/api/v1/api-token-auth/",
    logoutEndpoint: "/api/v1/logout/",
    paginateBy: 10
};

class BaseEntryHandler extends React.Component {

    componentDidMount() {
        this.props.app.loadEntries(true);
    }

    componentWillReceiveProps(nextProps) {
        var sameQuery = this.props.location.query === nextProps.location.query;
        if (!sameQuery) {
            this.props.app.loadEntries(true);
        }
    }

    render() {
        var entries = [];
        var handleEntryFavoriteClick = this.props.app.handleEntryFavoriteClick.bind(this.props.app);
        var providersByID = this.props.app.state.providersByID;
        this.props.app.state.entries.forEach(function(entry) {
            var provider = providersByID[entry.subscription.provider];
            entries.push(
                <Entry
                    entryId={entry.id}
                    title={entry.title}
                    url={entry.url}
                    permalink={entry.permalink}
                    content={entry.content}
                    isFavorite={entry.is_favorite}
                    source={entry.subscription.source}
                    providerID={entry.subscription.provider}
                    providerName={provider?provider.name:"?"}
                    handleFavoriteClick={handleEntryFavoriteClick}
                    key={entry.id}
                />
            )
        });

        return (
            <div className="content" ref="content">
                <Filter app={this.props.app} />
                <div className="entries">
                    {entries}
                </div>
                <Paginator
                    app={this.props.app}
                    paginateBy={this.props.app.props.paginateBy}
                    currentPage={this.props.app.state.currentPage}
                    totalCount={this.props.app.state.totalCount}
                    hasNext={this.props.app.state.hasNextPage}
                    hasPrev={this.props.app.state.hasPreviousPage}
                    loading={this.props.app.state.loading}
                />
            </div>
        );
    }
}

class HomeHandler extends React.Component {
    // use composition to separate home and main handlers
    render() {
        return <BaseEntryHandler app={this.props.app} {...this.props} />
    }
}

class EntryHandler extends React.Component {
    // use composition to separate home and main handlers
    render() {
        return <BaseEntryHandler app={this.props.app} {...this.props} />
    }
}

class CategoryFormHandler extends React.Component {

    render() {
        if (!this.props.app.state.initialized) {
            return null;
        }

        var category = null;

        var params = this.props.params;

        var categoryId = params["categoryId"] || null;
        if (categoryId) {
            // TODO: make better
            for (var i in this.props.app.state.categories) {
                category = this.props.app.state.categories[i];
                if (category["id"] == categoryId) {
                    break
                }
            }
        }
        return (
            <CategoryForm ref="category_form"
                createCategory={this.props.app.createCategory.bind(this.props.app)}
                updateCategory={this.props.app.updateCategory.bind(this.props.app)}
                deleteCategory={this.props.app.deleteCategory.bind(this.props.app)}
                category={category}
            />
        )
    }
}

class SubscriptionFormHandler extends React.Component {
    render() {
        if (!this.props.app.state.initialized) {
            return <div></div>
        }

        var providerId = this.props.app.props.params["providerId"];
        // TODO: make better
        var provider;
        for (var i in this.props.app.state.providers) {
            provider = this.props.app.state.providers[i];
            if (provider["id"] == providerId) {
                break
            }
        }

        var subscription = null;
        var subscriptionId = this.props.app.props.params["subscriptionId"];
        if (subscriptionId) {
            for (var i in provider["subscriptions"]) {
                subscription = provider["subscriptions"][i];
                if (subscription["id"] == subscriptionId) {
                    break
                }
            }
        }
        return (
            <SubscriptionForm ref="subscription_form"
                categories={this.props.app.state.categories}
                provider={provider}
                subscription={subscription}
                createSubscription={this.props.app.createSubscription.bind(this.props.app)}
                updateSubscription={this.props.app.updateSubscription.bind(this.props.app)}
                deleteSubscription={this.props.app.deleteSubscription.bind(this.props.app)}
            />
        )
    }
}

class ProfileHandler extends React.Component {
    render() {
        var telegramLink = null;
        if (this.props.app.state.telegramBotName) {
            var url = "https://telegram.me/" + this.props.app.state.telegram_bot_name + "?start=" + this.props.app.state.dashboard.uid;
            telegramLink = <a className="content-link" href={url}>Enable Telegram notifications</a>
        }
        return(
             <div className="form-container">
                <div className="form-header">Your dashboard</div>
                <div style={{"marginTop": "15px"}}>
                    {telegramLink}
                </div>
            </div>
        )
    }
}

ReactDOM.render(
    <Router history={browserHistory}>
        <Route path="/" component={App}>
            <IndexRoute name="home" component={HomeHandler} />
            <Route name="entry" path="dashboard/entry/" component={EntryHandler} />
            <Route name="category_create" path="dashboard/category/create/" component={CategoryFormHandler} />
            <Route name="category_edit" path="dashboard/category/:categoryId/edit/" component={CategoryFormHandler} />
            <Route name="subscription_create" path="dashboard/subscription/:providerId/create/" component={SubscriptionFormHandler} />
            <Route name="subscription_edit" path="dashboard/subscription/:providerId/:subscriptionId/edit/" component={SubscriptionFormHandler} />
            <Route name="profile" path="dashboard/profile/" component={ProfileHandler} />
        </Route>
    </Router>,
    document.querySelector("#app")
);
