import {
  Button,
  Center,
  Container,
  Group,
  MultiSelect,
  Stepper,
  Title,
  AppShell,
  Header,
  Slider,
  TextInput,
  Text,
  SimpleGrid,
  Loader,
  Modal,
  SegmentedControl,
  Input,
} from "@mantine/core";
import { useEffect, useState } from "react";
import ingredients from "@/data/ingredients.json";
import RecipeCard from "@/components/RecipeCard";
import {
  useDebouncedState,
  useDebouncedValue,
  useDisclosure,
} from "@mantine/hooks";
import { useQuery } from "react-query";
import { searchRecipe, searchRecipes } from "@/util/query";
import RecipeContent from "@/components/RecipeContent";
import { BaseRecipe, FullRecipe } from "@/util/types";

export default function Home() {
  // Stepper
  const [active, setActive] = useState(0);
  const handleStepChange = (nextStep: number) => {
    if (nextStep > 3 || nextStep < 0) return;
    setActive(nextStep);
  };

  // Query
  const [queryInput, setQueryInput] = useState("");
  const [query, setQuery] = useState<string[]>([]);

  // Ingredients MultiSelect
  const [pantry, setPantry] = useState<string[]>([]);

  // Misc Slider
  const [configValue, setSliderConfig] = useState<string>("mixed");

  // Modal
  const [selectedRecipe, setSelectedRecipe] = useState<
    FullRecipe | undefined
  >();
  const [selectedId, setSelectedId] = useState<number | undefined>();
  const [opened, { open, close }] = useDisclosure(false);

  const [queryDebounced] = useDebouncedValue(queryInput, 200);

  // Data Fetching
  const { isLoading: isLoadingQuery, data } = useQuery(
    ["recipesQuery", queryDebounced, pantry, configValue],
    async () => {
      return (await searchRecipes(queryDebounced, pantry, configValue)).data;
    }
  );

  const { isLoading: isLoadingRecipe, data: recipeData } = useQuery(
    ["selectedRecipe", selectedId],
    async () => {
      const placeholder: FullRecipe = {
        id: 1,
        name: "Test",
        description: "Testing 123 Lorem Ipsum idk",
        tags: ["cool", "idk", "hi"],
        minutes: 60,
        ingredients: ["fefw", "hiewfwf", "oiwef"],
        steps: ["Do this first", "Then This", "Then this"],
        img_link:
          "https://thewoksoflife.com/wp-content/uploads/2019/06/mapo-tofu-10.jpg",
        avg_rating: 4.5,
        user_data: [],
        food_URL: "food.com",
      };
      return placeholder;
      // if (selectedId) {
      //   return (await searchRecipe(selectedId)).data;
      // }
    }
  );

  return (
    <AppShell
      padding="md"
      header={
        <Header height={70} px="lg" py="md">
          <Center>
            <Title order={2}>Asian Food Recs</Title>
          </Center>
        </Header>
      }
      navbar={
        // <Navbar width={{ base: 300 }} height={500} p="xs">
        //   <Navbar.Section mt="xs">
        //     <MainLinks />
        //   </Navbar.Section>
        // </Navbar>
        <></>
      }
      styles={(theme) => ({
        main: {
          backgroundColor:
            theme.colorScheme === "dark"
              ? theme.colors.dark[8]
              : theme.colors.gray[0],
        },
      })}
    >
      <Modal size="xl" opened={opened} onClose={close} title="Details">
        {/* {recipeData ? <RecipeContent recipe={recipeData} /> : <Loader />} */}
        {selectedRecipe ? (
          <RecipeContent recipe={selectedRecipe} />
        ) : (
          <Loader />
        )}
      </Modal>

      <Container p="lg" size="sm">
        <TextInput
          value={queryInput}
          onChange={(event) => setQueryInput(event.currentTarget.value)}
          label="What's on your mind?"
          placeholder="chicken, spicy, stir fry, with rice, high fiber"
          withAsterisk
          mb="xl"
        />
        <MultiSelect
          value={pantry}
          onChange={setPantry}
          data={ingredients}
          label="What's in your pantry?"
          placeholder="no need for exact matches!"
          limit={20}
          maxDropdownHeight={160}
          searchable
          creatable
          onCreate={(newItem) => {
            setPantry((current) => [...current, newItem]);
            return newItem;
          }}
          transitionProps={{
            duration: 150,
            transition: "pop-top-left",
            timingFunction: "ease",
          }}
        />
        <Group position="left" mt="xl">
          <Input.Label>How should we use your pantry?</Input.Label>
        </Group>
        <SegmentedControl
          value={configValue}
          data={[
            {
              label: "Incorporate All",
              value: "includesIng",
            },
            {
              label: "Interested In",
              value: "mixed",
            },
            {
              label: "Only Include",
              value: "onlyTheseIng",
            },
          ]}
          onChange={setSliderConfig}
        />
      </Container>
      <Container p="lg" size="lg">
        <Center>
          <Title order={2}>Recipes</Title>
        </Center>
        <Center mt="md">{isLoadingQuery && <Loader />}</Center>
        <Center mt="md">
          {data && !data.length && (
            <Text>Found 0 recipes given your search criteria.</Text>
          )}
        </Center>
        <SimpleGrid
          breakpoints={[
            { minWidth: "sm", cols: 1 },
            { minWidth: "md", cols: 2 },
            { minWidth: 1200, cols: 3 },
          ]}
          mt="md"
        >
          {data?.map((recipe) => (
            <RecipeCard
              key={recipe.name}
              recipe={recipe}
              detailCallback={() => {
                setSelectedId(recipe.id);
                setSelectedRecipe(recipe);
                open();
              }}
            />
          ))}
        </SimpleGrid>
      </Container>
    </AppShell>
  );
}
