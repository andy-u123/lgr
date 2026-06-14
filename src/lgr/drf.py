from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, viewsets
from rest_framework import filters as rf_filters
from rest_framework import routers

from lgr import models, filters


router = routers.DefaultRouter()


class BarcodeSerializer(serializers.HyperlinkedModelSerializer):
    item_name = serializers.ReadOnlyField(source="item.name", read_only=True)
    item_description = serializers.ReadOnlyField(
        source="item.description", read_only=True
    )

    class Meta:
        model = models.Barcode
        fields = (
            "code",
            "parent",
            "owner",
            "item",
            "description",
            "item_name",
            "item_description",
            "api_child_names",
            "api_parent_names",
            "api_loan_info",
            "api_history",
        )


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Person
        fields = "__all__"


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Item
        fields = "__all__"


class LoanSerializer(serializers.ModelSerializer):
    person_name = serializers.ReadOnlyField(source="person.nickname")

    class Meta:
        model = models.Loan
        fields = "__all__"


class BarcodeViewSet(viewsets.ModelViewSet):
    queryset = models.Barcode.objects.all()
    serializer_class = BarcodeSerializer
    search_fields = ("code", "item__name", "description", "item__description")
    filter_backends = (
        filters.QuickSearchFilter,
        rf_filters.OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_fields = {"parent": ["exact", "isnull"], "owner": ["exact", "isnull"]}


class PersonViewSet(viewsets.ModelViewSet):
    queryset = models.Person.objects.all()
    serializer_class = PersonSerializer
    search_fields = ("nickname",)


class ItemViewSet(viewsets.ModelViewSet):
    queryset = models.Item.objects.all()
    serializer_class = ItemSerializer
    search_fields = ("name",)
    filter_backends = (rf_filters.SearchFilter, DjangoFilterBackend)
    filterset_fields = {"barcodes": ["isnull"]}


class TagViewSet(viewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = ItemSerializer


class LoanViewSet(viewsets.ModelViewSet):
    queryset = models.Loan.objects.order_by("-id")
    serializer_class = LoanSerializer
    filter_backends = (filters.field_search_filter("person__id"), DjangoFilterBackend)
    filterset_fields = {"status": ["exact"]}


class UserLoanViewSet(viewsets.ModelViewSet):
    queryset = models.Loan.objects.order_by("-id")
    serializer_class = LoanSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = {"status": ["exact"]}

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(person__nickname__exact=user)


router.register("barcodes", BarcodeViewSet)
router.register("persons", PersonViewSet)
router.register("items", ItemViewSet)
router.register("tags", TagViewSet)
router.register("loans", LoanViewSet)
router.register("my_loans", UserLoanViewSet)
