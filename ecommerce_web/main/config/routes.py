from flask_restful import Api

# Admin Auth Resources
from main.v1.admin.auth.auth_resource import AdminRegistrationResource, AdminLoginResource
from main.v1.admin.auth.profile_resource import AdminProfileResource

# Admin Dashboard Resources
from main.v1.admin.dashboard.users.user_resource import UserListResource, UserResource
from main.v1.admin.dashboard.order.order_resource import OrderListResource, OrderResource

# Customer Auth Resources
from main.v1.customer.auth.auth_resource import CustomerRegistrationResource, CustomerLoginResource
from main.v1.customer.auth.profile_resource import CustomerProfileResource

# Customer Order, Wishlist & Invoice Resources
from main.v1.customer.order.order_resource import PlaceOrderResource
from main.v1.customer.wishlist.wishlist import WishlistResource
from main.v1.customer.invoice.invoice_resource import InvoiceResource

# Service Provider Auth, Order, Notification, Product Resources
from main.v1.service_provider.auth.auth_resource import ProviderRegistrationResource, ProviderLoginResource
from main.v1.service_provider.auth.profile_resource import ProviderProfileResource
from main.v1.service_provider.order.order_resource import ProviderViewOrdersResource, ProviderUpdateOrderStatusResource
from main.v1.service_provider.notification.notification_resource import ProviderViewNotificationsResource, ProviderCreateNotificationResource
from main.v1.service_provider.product.product_resource import ProviderAddProductResource, ProviderViewProductsResource, ProviderUpdateProductResource, ProviderDeleteProductResource


def register_routes(app):
    api = Api(app, prefix="/api/v1")

    # Admin Routes
    api.add_resource(AdminRegistrationResource, '/admin/auth/register')
    api.add_resource(AdminLoginResource, '/admin/auth/login')
    api.add_resource(AdminProfileResource, '/admin/auth/profile')

    api.add_resource(UserListResource, '/admin/dashboard/users')
    api.add_resource(UserResource, '/admin/dashboard/users/<int:user_id>')
    api.add_resource(OrderListResource, '/admin/dashboard/orders')
    api.add_resource(OrderResource, '/admin/dashboard/orders/<int:order_id>')

    # Customer Routes
    api.add_resource(CustomerRegistrationResource, '/customer/auth/register')
    api.add_resource(CustomerLoginResource, '/customer/auth/login')
    api.add_resource(CustomerProfileResource, '/customer/auth/profile')

    api.add_resource(PlaceOrderResource, '/customer/order')
    api.add_resource(WishlistResource, '/customer/wishlist')
    api.add_resource(InvoiceResource, "/customer/invoice/<int:order_id>")

    # Service Provider Routes
    api.add_resource(ProviderRegistrationResource, "/service_provider/auth/register")
    api.add_resource(ProviderLoginResource, '/service_provider/auth/login')
    api.add_resource(ProviderProfileResource, '/service_provider/auth/profile')

    api.add_resource(ProviderViewOrdersResource, '/service_provider/orders')
    api.add_resource(ProviderUpdateOrderStatusResource, '/service_provider/orders/<int:order_id>/status')

    api.add_resource(ProviderViewNotificationsResource, '/service_provider/notifications')
    api.add_resource(ProviderCreateNotificationResource, '/service_provider/notifications')

    api.add_resource(ProviderAddProductResource, '/service_provider/products')
    api.add_resource(ProviderViewProductsResource, '/service_provider/products')
    api.add_resource(ProviderUpdateProductResource, '/service_provider/products/<int:product_id>')
    api.add_resource(ProviderDeleteProductResource, '/service_provider/products/<int:product_id>')
