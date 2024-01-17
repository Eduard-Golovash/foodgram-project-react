from rest_framework import serializers
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField

from users.models import User
from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    ShoppingList,
    Favorite,
    RecipeIngredient,
)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request_user = self.context['request'].user
        if request_user.is_authenticated:
            return obj != request_user and request_user.subscribers.filter(id=obj.id).exists()
        return False

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context['request'].user
        if not user.is_authenticated:
            data.pop('is_subscribed', None)

        return data


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'password')


class CustomSetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'quantity')


class RecipeListSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True, default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientSerializer(many=True, read_only=True, source='recipe_ingredients')
    # is_favorited = serializers.SerializerMethodField()
    is_in_shopping_list = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Favorite.objects.filter(
                user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_list(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return ShoppingList.objects.filter(
                user=user, recipe=obj).exists()
        return False

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context['request'].user
        if user.is_authenticated:
            data['is_favorited'] = Favorite.objects.filter(
                user=user, recipe=instance).exists()
        else:
            data.pop('is_favorited', None)
        return data


class QuantitySerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField()
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'quantity')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    ingredients = QuantitySerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError({
                'ingredients': 'Должен быть хотя бы 1 ингредиент'})
        ingredients_list = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError({
                    'ingredients': 'Ингредиенты должны быть уникальными'})
            if int(item['quantity']) <= 0:
                raise ValidationError({
                    'quantity': 'Количество должно быть > 0'})
            ingredients_list.append(ingredient)
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError({'tags': 'Должен быть хотя бы 1 тег'})
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError({'tags': 'Теги должны быть уникальными'})
            tags_list.append(tag)
        return tags

    def create(self, validated_data):
        print("Validated Data:", validated_data)
        tags = validated_data.pop('tags')
        print("Validated Tags:", tags)
        ingredients = validated_data.pop('ingredients')
        print("Validated Ing:", ingredients)
        recipe = Recipe.objects.create(**validated_data)
        self.add_tags(tags, recipe)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            instance.tags.set(validated_data.pop('tags'))
        if 'ingredients' in validated_data:
            instance.recipe_ingredients.all().delete()
            self.add_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)

    def add_tags(self, tags, recipe):
        recipe.tags.set(tags)

    def add_ingredients(self, ingredients, recipe):
        for item in ingredients:
            ingredient = item['id']
            quantity = item['quantity']
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient,
                quantity=quantity
            )

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer()

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def create(self, validated_data):
        recipe_data = validated_data.pop('recipe')
        recipe = Recipe.objects.create(**recipe_data)
        favorite = Favorite.objects.create(recipe=recipe, **validated_data)
        return favorite

    def update(self, instance, validated_data):
        recipe_data = validated_data.pop('recipe')
        instance.recipe.name = recipe_data.get('name', instance.recipe.name)
        instance.recipe.image = recipe_data.get('image', instance.recipe.image)
        instance.recipe.cooking_time = recipe_data.get(
            'cooking_time', instance.recipe.cooking_time)
        instance.recipe.save()
        instance.save()
        return instance


class ShoppingListSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer()

    class Meta:
        model = ShoppingList
        fields = '__all__'


class DownloadShoppingCartSerializer(serializers.Serializer):
    ingredient_name = serializers.CharField()
    total_quantity = serializers.IntegerField()
    measurement_unit = serializers.CharField()


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        print(f"Current user: {request.user}")
        if request and request.user.is_authenticated:
            subscribed = obj.subscribers.filter(user=request.user).exists()
            print(f"Is subscribed: {subscribed}")
            return subscribed
        return False

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data


class SubscriptionActionSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def validate(self, obj):
        request = self.context.get('request')
        if request and (request.user == obj):
            raise serializers.ValidationError({'errors': 'Ошибка подписки.'})
        return obj

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request and request.user.is_authenticated
            and obj.subscribers.filter(user=request.user).exists()
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoriteListSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer()

    class Meta:
        model = Favorite
        fields = ('recipe',)