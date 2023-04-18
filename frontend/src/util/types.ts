export type BaseRecipe = {
  id: number;
  name: string;
  description: string;
  tags: string[];
  minutes: number;
  ingredients: string[];
  steps: string[];
  img_link: string;
};

export type FullRecipe = BaseRecipe & {};
